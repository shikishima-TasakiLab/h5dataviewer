# -*- coding: utf-8 -*-

import os
from typing import Any, Dict, List, Optional, Union
import argparse
import sys

import pyqtgraph as pg
from pyqtgraph.opengl import GLViewWidget, GLScatterPlotItem
from PySide2.QtGui import QBrush, QColor, QImage, QPixmap
import numpy as np
import h5py
import cv2
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from pyqtgraph.opengl.items.GLGridItem import GLGridItem
from scipy.spatial.transform import Rotation
from PySide2.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QMainWindow, QSizePolicy, QSpacerItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PySide2.QtCore import Qt
from pyqtgraph.opengl.items.GLLinePlotItem import GLLinePlotItem

from .ui import Ui_MainWindow
from .structure import *
from .GLTextItem import GLTextItem

CONFIG_FILE:str = 'file'
CONFIG_RANGE_MIN:str = 'range-min'
CONFIG_RANGE_MAX:str = 'range-max'
CONFIG_AXIS_WIDTH:str = 'axis-width'
CONFIG_AXIS_SIZE:str = 'axis-size'
CONFIG_PREVIEW_WIDTH:str = 'preview-width'
CONFIG_PREVIEW_HEIGHT:str = 'preview-height'
COLOR_RED:np.ndarray = np.array([1.0, 0.0, 0.0, 1.0])
COLOR_GREEN:np.ndarray = np.array([0.0, 1.0, 0.0, 1.0])
COLOR_BLUE:np.ndarray = np.array([0.0, 0.0, 1.0, 1.0])
COLOR_TF:np.ndarray = np.array([0.5, 0.5, 0.5, 1.0])

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent=None) -> None:
        QTreeWidgetItem.__init__(self, parent)
    
    def __lt__(self, otherItem:QTreeWidgetItem):
        column = self.treeWidget().sortColumn()
        try:
            return float(self.text(column)) < float(otherItem.text(column))
        except ValueError:
            return self.text(column) < otherItem.text(column)

class H5DataViewer(QMainWindow):
    config:Dict[str, Union[float, dict]] = {}
    h5file:h5py.File = None

    def __init__(self, parent=None) -> None:
        super(H5DataViewer, self).__init__()
        self.parse()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionExit.triggered.connect(lambda: self.close())
        self.ui.viewButton.clicked.connect(lambda: self.exec_view_dialog())

        self.axis_obj = np.array([
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]
        ], dtype=np.float32) * self.config[CONFIG_AXIS_SIZE]

        self.axis_color = np.stack([COLOR_RED, COLOR_RED, COLOR_GREEN, COLOR_GREEN, COLOR_BLUE, COLOR_BLUE], axis=0)
        self.tf_color = np.stack([COLOR_TF, COLOR_TF], axis=0)

        self.loadH5()
    
    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('file', type=str)
        parser.add_argument('--preview-width', type=int, default=512)
        parser.add_argument('--preview-height', type=int, default=256)
        parser.add_argument('--tf-axis-size', type=float, default=1.0)
        parser.add_argument('--tf-axis-width', type=float, default=5.0)
        parser.add_argument('--range-min', type=float, default=0.0)
        parser.add_argument('--range-max', type=float, default=100.0)
    
        args = parser.parse_args()
        self.config[CONFIG_FILE] = args.file
        self.config[CONFIG_PREVIEW_WIDTH] = args.preview_width
        self.config[CONFIG_PREVIEW_HEIGHT] = args.preview_height
        self.config[CONFIG_AXIS_SIZE] = args.tf_axis_size
        self.config[CONFIG_AXIS_WIDTH] = args.tf_axis_width
        self.config[CONFIG_RANGE_MIN] = args.range_min
        self.config[CONFIG_RANGE_MAX] = args.range_max
    
    def __Del__(self):
        if self.h5file:
            self.h5file.close()

    def loadH5(self):
        if self.h5file:
            self.h5file.close()
        self.h5file = h5py.File(self.config[CONFIG_FILE], 'r')

        # "Label"タブの設定
        if isinstance(self.h5file.get(H5_KEY_LABEL), h5py.Group):
            def decide_textColor(red, green, blue):
                if red * 0.299 + green * 0.587 + blue * 0.114 < 186:
                    return Qt.white
                else:
                    return Qt.black

            h5_label:h5py.Group = self.h5file[H5_KEY_LABEL]
            self.config[H5_KEY_LABEL] = {}
            for label_key, label_item in h5_label.items():
                label_widget = QWidget()
                label_layout = QHBoxLayout(label_widget)
                label_tree = QTreeWidget(label_widget)
                label_tree.setHeaderLabels(['Index', 'Tag', 'R', 'G', 'B', ''])
                label_tree.setSortingEnabled(True)
                label_tree.sortByColumn(0, Qt.AscendingOrder)
                label_layout.addWidget(label_tree)
                self.ui.labelTab.addTab(label_widget, label_key)

                label_colors:Dict[str, np.ndarray] = {}
                for label_idx_key, label_idx_item in label_item.items():
                    label_idx_name:Union[bytes, str] = label_idx_item[SUBTYPE_NAME][()]
                    label_idx_name = label_idx_name.decode() if isinstance(label_idx_name, bytes) else label_idx_name
                    label_idx_color:h5py.Dataset = label_idx_item[TYPE_COLOR]
                    red = label_idx_color[()][2]
                    green = label_idx_color[()][1]
                    blue = label_idx_color[()][0]
                    label_colors[label_idx_key] = label_idx_color[()]
                    label_tree_item = TreeWidgetItem([label_idx_key, label_idx_name, str(red), str(green), str(blue)])
                    label_tree_item.setBackground(1, QBrush(QColor('#%02X%02X%02X'%(red, green, blue))))
                    label_tree_item.setForeground(1, QBrush(decide_textColor(red, green, blue)))
                    label_tree_item.setTextAlignment(0, Qt.AlignRight | Qt.AlignVCenter)
                    label_tree_item.setTextAlignment(2, Qt.AlignRight | Qt.AlignVCenter)
                    label_tree_item.setTextAlignment(3, Qt.AlignRight | Qt.AlignVCenter)
                    label_tree_item.setTextAlignment(4, Qt.AlignRight | Qt.AlignVCenter)
                    label_tree.addTopLevelItem(label_tree_item)
                self.config[H5_KEY_LABEL][label_key] = label_colors

        # "Data"タブの設定
        self.ui.dataTree.setSortingEnabled(True)
        self.ui.dataTree.sortByColumn(0, Qt.AscendingOrder)
        self.add_datatree(self.h5file, self.ui.dataTree)

        # "Preview"領域の設定
        def get_h5keys(h5obj:Union[h5py.Group, h5py.Dataset], dst_paths:List[str]=[], path:str='') -> None:
            for key, item in h5obj.items():
                joined_path = os.path.join(path, key)
                if item.attrs.get(H5_ATTR_TYPE) is not None:
                    dst_paths.append(joined_path)
                    continue
                elif isinstance(item, h5py.Group):
                    get_h5keys(item, dst_paths, joined_path)

        self.config['preview'] = {}
        preview_key_list:List[str] = []
        get_h5keys(self.h5file[H5_KEY_DATA + '/0'], preview_key_list)
        
        itr:int = 0
        pose_flag:bool = False
        for preview_key in preview_key_list:
            preview_dict:Dict[str, Union[QLabel, GLViewWidget]] = {}
            
            data_type:str = convert_str(self.h5file[H5_KEY_DATA + '/0/' + preview_key].attrs.get(H5_ATTR_TYPE))
            preview_dict['type'] = data_type
            if {data_type} <= {TYPE_MONO8, TYPE_MONO16, TYPE_BGR8, TYPE_RGB8, TYPE_BGRA8, TYPE_RGBA8, TYPE_DEPTH, TYPE_SEMANTIC2D}:
                preview_layout = QVBoxLayout(self.ui.dataWidget)
                preview_label = QLabel(preview_key)
                preview_layout.addWidget(preview_label)
                preview_dict['widget'] = QLabel(self.ui.dataWidget)
                preview_layout.addWidget(preview_dict['widget'])
                self.config_preview_func(data_type, preview_dict)
                self.config['preview'][preview_key] = preview_dict
                preview_layout.addStretch(0)
                self.ui.previewLayout.addLayout(preview_layout, itr // 2, itr % 2)
                itr += 1
            elif {data_type} <= {TYPE_POINTS, TYPE_SEMANTIC3D, TYPE_POSE}:
                if data_type == TYPE_POSE:
                    if pose_flag is True: continue
                    else: pose_flag = True
                    preview_key = 'pose'
                preview_label = QLabel(preview_key)
                preview_layout = QVBoxLayout(self.ui.dataWidget)
                self.ui.previewLayout.addLayout(preview_layout, itr // 2, itr % 2)
                preview_layout.addWidget(preview_label)
                preview_dict['widget'] = GLViewWidget(self.ui.dataWidget)
                preview_dict['widget'].setFixedSize(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT])
                axis_item = GLLinePlotItem(pos=self.axis_obj, color=self.axis_color, width=self.config[CONFIG_AXIS_WIDTH], mode='lines')
                preview_dict['widget'].addItem(axis_item)
                preview_layout.addWidget(preview_dict['widget'])
                preview_dict['item'] = GLScatterPlotItem(size=1)
                preview_dict['widget'].addItem(preview_dict['item'])
                self.config_preview_func(data_type, preview_dict)
                self.config['preview'][preview_key] = preview_dict
                preview_layout.addStretch(0)
                itr += 1

        # "Transform"タブの設定
        self.pose_dict = {}
        for key_tag, item_tag in self.h5file['/data/0'].items():
            self.get_nestpose(self.pose_dict, key_tag, item_tag)
        for key_root, item_root in self.h5file.items():
            if key_root in [H5_KEY_HEADER, H5_KEY_DATA, H5_KEY_LABEL]: continue
            for key_tag, item_tag in item_root.items():
                self.get_nestpose(self.pose_dict, key_tag, item_tag, key_root='/' + key_root)
        pose_parents = {ps[CONFIG_TAG_FRAMEID] for ps in self.pose_dict.values()}
        pose_children = {ps[CONFIG_TAG_CHILDFRAMEID] for ps in self.pose_dict.values()}
        pose_roots = pose_parents - pose_children
        pose_nodes = {}
        for ps in self.pose_dict.values():
            pose_nodes[ps[CONFIG_TAG_CHILDFRAMEID]] = {}
        self.tf_tree_dict = {}
        for ps in self.pose_dict.values():
            child_frame_id = ps[CONFIG_TAG_CHILDFRAMEID]
            frame_id = ps[CONFIG_TAG_FRAMEID]
            node = pose_nodes[child_frame_id]
            if {frame_id} <= pose_roots:
                if frame_id not in self.tf_tree_dict.keys():
                    self.tf_tree_dict[frame_id] = {}
                parent = self.tf_tree_dict[frame_id]
            else:
                parent = pose_nodes[frame_id]
            parent[child_frame_id] = node
        
        def setTftree(parentitem:TreeWidgetItem, tree_config:Dict[str, Union[str, dict]]):
            for key_frameid, item_frameid in tree_config.items():
                data = self.pose_dict[key_frameid][CONFIG_TAG_KEY]
                item = TreeWidgetItem([key_frameid, data])
                parentitem.addChild(item)
                setTftree(item, item_frameid)
                item.setExpanded(True)
        
        for key_frameid, item_frameid in self.tf_tree_dict.items():
            item = TreeWidgetItem([key_frameid])
            self.ui.tfTree.addTopLevelItem(item)
            setTftree(item, item_frameid)
            item.setExpanded(True)

        # "Preview"領域の初期表示
        self.ui.previewIndexLabel.setText('0')
        for preview_key, preview_config in self.config['preview'].items():
            if preview_config['type'] == TYPE_POSE:
                preview_key = ''
            preview_config['func'](self.h5file[os.path.join('/data/0', preview_key)], preview_config)

        self.ui.dataTree.itemSelectionChanged.connect(lambda: self.dataTree_selectionChanged())

    def add_datatree(self, h5obj:Union[h5py.File, h5py.Group], treeitem:Union[QTreeWidget, QTreeWidgetItem], indent:str='') -> None:
        for key, obj in h5obj.items():
            print('\r{0}- {1:<30s}'.format(indent, key), end='')
            if isinstance(obj, h5py.Group):
                data_type = obj.attrs.get(H5_ATTR_TYPE)
                if data_type is not None:
                    data_type = convert_str(data_type)
                else:
                    data_type = 'Group'
                item_child = TreeWidgetItem([key, data_type, ''])
                self.add_datatree(obj, item_child, indent + '  ')
            elif isinstance(obj, h5py.Dataset):
                data = str(obj[()]) if obj.ndim <= 1 else ''
                data_type = obj.attrs.get(H5_ATTR_TYPE)
                if data_type is not None:
                    data_type = convert_str(data_type)
                item_child = TreeWidgetItem([key, str(data_type), str(type(obj[()])), data])
            else:
                continue
            if isinstance(treeitem, QTreeWidget):
                treeitem.addTopLevelItem(item_child)
            elif isinstance(treeitem, QTreeWidgetItem):
                treeitem.addChild(item_child)
            else:
                continue

    def config_view_dialog(self, data_type:str, config:Dict[str, Union[QLabel, GLViewWidget, GLScatterPlotItem]]) -> None:
        self.viewDialog = QDialog(self)
        self.viewDialog.resize(800, 600)
        view_layout = QVBoxLayout(self.viewDialog)
        if {data_type} <= {TYPE_MONO8, TYPE_MONO16, TYPE_BGR8, TYPE_RGB8, TYPE_BGRA8, TYPE_RGBA8, TYPE_DEPTH, TYPE_SEMANTIC2D}:
            view_widget = QLabel()
            view_layout.addWidget(view_widget)
            config['widget'] = view_widget
            self.config_preview_func(data_type, config)
        elif {data_type} <= {TYPE_POINTS, TYPE_SEMANTIC3D, TYPE_POSE}:
            view_widget = GLViewWidget(self.viewDialog)
            view_layout.addWidget(view_widget)
            config['widget'] = view_widget
            axis_item = GLLinePlotItem(pos=self.axis_obj, color=self.axis_color, width=self.config[CONFIG_AXIS_WIDTH], mode='lines')
            view_widget.addItem(axis_item)
            view_item = GLScatterPlotItem(size=1)
            view_widget.addItem(view_item)
            config['item'] = view_item
            self.config_preview_func(data_type, config)
    
    def config_preview_func(self, data_type:str, config:Dict[str, str]):
        if data_type == TYPE_MONO8:
            config['func'] = self.__preview_mono8
        elif data_type == TYPE_MONO16:
            config['func'] = self.__preview_mono16
        elif data_type == TYPE_BGR8:
            config['func'] = self.__preview_bgr8
        elif data_type == TYPE_RGB8:
            config['func'] = self.__preview_rgb8
        elif data_type == TYPE_BGRA8:
            config['func'] = self.__preview_bgra8
        elif data_type == TYPE_RGBA8:
            config['func'] = self.__preview_rgba8
        elif data_type == TYPE_DEPTH:
            config['func'] = self.__preview_depth
        elif data_type == TYPE_SEMANTIC2D:
            config['func'] = self.__preview_semantic2d
        elif data_type == TYPE_POINTS:
            config['func'] = self.__preview_points
        elif data_type == TYPE_SEMANTIC3D:
            config['func'] = self.__preview_semantic3d
        elif data_type == TYPE_POSE:
            config['func'] = self.__preview_pose

    def exec_view_dialog(self):
        item = self.ui.dataTree.selectedItems()[0]
        path = self.__restore_path(item)
        data_type = self.h5file[path].attrs.get(H5_ATTR_TYPE)
        config:Dict[str, Union[QLabel, GLScatterPlotItem]] = {}
        self.config_view_dialog(data_type, config)
        config['func'](self.h5file[path], config)
        self.viewDialog.exec()

    def get_nestpose(self, config_pose:Dict[str, Dict[str, str]], key_tag:str, item_tag:Union[h5py.Dataset, h5py.Group], key_root:str=''):
        """get_nestpose

        HDF5の入れ子から'pose'データを取得する

        Args:
            config_pose (list): 設定用の辞書
            key_tag (str): HDF5のキー
            item_tag (Union[h5py.Dataset, h5py.Group]): HDF5のアイテム
            key_root (str, optional): 辞書に登録する際の親キー. Defaults to ''.
        """
        key = os.path.join(key_root ,key_tag)
        if isinstance(item_tag, h5py.Group):
            data_type:Union[str, bytes] = item_tag.attrs.get(H5_ATTR_TYPE)
            data_type = data_type.decode() if isinstance(data_type, bytes) else data_type
            if data_type in [TYPE_POSE]:
                frame_id:Union[str, bytes] = item_tag.attrs.get(H5_ATTR_FRAMEID)
                frame_id = frame_id.decode() if isinstance(frame_id, bytes) else frame_id
                child_frame_id:Union[str, bytes] = item_tag.attrs.get(H5_ATTR_CHILDFRAMEID)
                child_frame_id = child_frame_id.decode() if isinstance(child_frame_id, bytes) else child_frame_id

                config_pose_dict = {}
                config_pose_dict[CONFIG_TAG_KEY] = key
                config_pose_dict[CONFIG_TAG_FRAMEID] = frame_id
                config_pose_dict[CONFIG_TAG_CHILDFRAMEID] = child_frame_id
                config_pose[child_frame_id] = config_pose_dict

            for key_child, item_child in item_tag.items():
                self.get_nestpose(config_pose, key_child, item_child, key)

    def __restore_path(self, item:QTreeWidgetItem) -> str:
        parent = item.parent()
        if parent is None:
            parent_path = ''
        else:
            parent_path = self.__restore_path(parent)
        return os.path.join(parent_path, item.text(0))
        
    def dataTree_selectionChanged(self) -> None:
        self.ui.attrTree.clear()
        item = self.ui.dataTree.selectedItems()[0]
        path = self.__restore_path(item)

        if isinstance(self.h5file[path], h5py.Dataset):
            attrItem = TreeWidgetItem(['(shape)', str(self.h5file[path].shape)])
            self.ui.attrTree.addTopLevelItem(attrItem)
            attrItem = TreeWidgetItem(['(ndim)', str(self.h5file[path].ndim)])
            self.ui.attrTree.addTopLevelItem(attrItem)
            attrItem = TreeWidgetItem(['(dtype)', str(self.h5file[path].dtype)])
            self.ui.attrTree.addTopLevelItem(attrItem)
        
        for key, obj in self.h5file[path].attrs.items():
            attrItem = TreeWidgetItem([key, str(obj)])
            self.ui.attrTree.addTopLevelItem(attrItem)
        
        data_type = self.h5file[path].attrs.get(H5_ATTR_TYPE)
        if data_type is None:
            self.ui.viewButton.setEnabled(False)
        elif {data_type} <= {TYPE_MONO8, TYPE_MONO16, TYPE_BGR8, TYPE_RGB8, TYPE_BGRA8, TYPE_RGBA8, TYPE_DEPTH, TYPE_SEMANTIC2D, TYPE_POINTS, TYPE_SEMANTIC3D, TYPE_POSE}:
            self.ui.viewButton.setEnabled(True)
        else:
            self.ui.viewButton.setEnabled(False)

        if path.find('data/') == 0:
            idx = path.split('/')[1]
            self.ui.previewIndexLabel.setText(idx)
            for preview_key, preview_config in self.config['preview'].items():
                if preview_config['type'] == TYPE_POSE:
                    preview_key = ''
                preview_config['func'](self.h5file[os.path.join('/data', idx, preview_key)], preview_config)

    def __preview_mono8(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img:np.ndarray = h5data[()]
        h, w = img.shape[:2]
        qimg = QImage(img.flatten(), w, h, QImage.Format_Grayscale8)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_mono16(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img:np.ndarray = h5data[()]
        h, w = img.shape[:2]
        qimg = QImage(img.flatten(), w, h, QImage.Format_Grayscale16)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_bgr8(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img:np.ndarray = h5data[()]
        h, w = img.shape[:2]
        qimg = QImage(img.data, w, h, QImage.Format_BGR888)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_rgb8(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img:np.ndarray = h5data[()]
        h, w = img.shape[:2]
        qimg = QImage(img.data, w, h, QImage.Format_RGB888)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_bgra8(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img:np.ndarray = cv2.cvtColor(h5data[()], cv2.COLOR_BGRA2RGBA)
        h, w = img.shape[:2]
        qimg = QImage(img.data, w, h, QImage.Format_RGBA8888)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_rgba8(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img:np.ndarray = h5data[()]
        h, w = img.shape[:2]
        qimg = QImage(img.data, w, h, QImage.Format_RGBA8888)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_depth(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        img = h5data[()]
        range_min = self.config[CONFIG_RANGE_MIN]
        range_max = self.config[CONFIG_RANGE_MAX]

        img_normalized:np.ndarray = (img - range_min) * 255. / (range_max - range_min)
        img_normalized_8bit:np.ndarray = 255 - np.uint8(img_normalized)
        img_colored:np.ndarray = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        img_colored = cv2.applyColorMap(img_normalized_8bit, cv2.COLORMAP_JET)
        img_colored[np.where((img < range_min) | (range_max < img))] = np.array([0, 0, 0], dtype=np.uint8)
        h, w = img_colored.shape[:2]
        qimg = QImage(img_colored.data, w, h, QImage.Format_BGR888)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))
        
    def __preview_semantic2d(self, h5data:h5py.Dataset, config:Dict[str, QLabel]):
        src:np.ndarray = h5data[()]
        dst:np.ndarray = np.zeros((src.shape[0], src.shape[1], 3), dtype=np.uint8)
        label_tag:str = h5data.attrs.get(H5_ATTR_LABELTAG)
        label_config:Dict[str, np.ndarray] = self.config[H5_KEY_LABEL][label_tag]

        for key, color in label_config.items():
            dst[np.where(src == int(key))] = color
        h, w = dst.shape[:2]
        qimg = QImage(dst.data, w, h, QImage.Format_BGR888)
        config['widget'].setPixmap(QPixmap.fromImage(qimg).scaled(self.config[CONFIG_PREVIEW_WIDTH], self.config[CONFIG_PREVIEW_HEIGHT], Qt.KeepAspectRatio, Qt.FastTransformation))

    def __preview_points(self, h5data:h5py.Dataset, config:Dict[str, GLScatterPlotItem]):
        src:np.ndarray = h5data[()]
        config['item'].setData(pos=src, color=(1.0, 1.0, 1.0, 0.2))

    def __preview_semantic3d(self, h5data:h5py.Group, config:Dict[str, GLScatterPlotItem]):
        points = h5data[TYPE_POINTS][()]
        semantic1d = h5data[TYPE_SEMANTIC1D][()]
        label_tag:str = h5data.attrs.get(H5_ATTR_LABELTAG)
        label_config:Dict[str, np.ndarray] = self.config[H5_KEY_LABEL][label_tag]

        semantic_color = np.zeros((semantic1d.shape[0], 4), np.float32)
        for key, color in label_config.items():
            semantic_color[np.where(semantic1d == int(key))] = np.append(np.flip(np.float32(color / 255.)), [1.0])
        config['item'].setData(pos=points, color=semantic_color)

    def __draw_tf(self, config:Dict[str, GLViewWidget], frame_id:str, tf:Tuple[np.ndarray, Rotation]=(np.zeros((3,), dtype=np.float32), Rotation.from_quat([0.0, 0.0, 0.0, 1.0])), parent_tf:Tuple[np.ndarray, Rotation]=(np.zeros((3,), dtype=np.float32), Rotation.from_quat([0.0, 0.0, 0.0, 1.0]))):
        if np.any(tf[0] != parent_tf[0]):
            tf_line:np.ndarray = np.stack([parent_tf[0], tf[0]], axis=0)
            item = GLLinePlotItem(pos=tf_line, color=self.tf_color, width=1.0, mode='lines')
            config['widget'].addItem(item)

        item = GLLinePlotItem(
            pos=tf[1].apply(self.axis_obj) + tf[0],
            color=self.axis_color,
            width=self.config[CONFIG_AXIS_WIDTH], mode='lines'
        )
        config['widget'].addItem(item)
        item = GLTextItem(pos=(float(tf[0][0]), float(tf[0][1]), float(tf[0][2])), text=frame_id)
        config['widget'].addItem(item)

    def __preview_pose(self, h5data:h5py.Group, config:Dict[str, GLViewWidget]):
        def draw_nest_tf(key:str, children:Dict[str, dict], config:Dict[str, GLViewWidget], parent_tf:Tuple[np.ndarray, Rotation]=(np.zeros((3,), dtype=np.float32), Rotation.from_quat([0.0, 0.0, 0.0, 1.0]))):
            pose_data = self.pose_dict.get(key)
            if pose_data is None:
                tr:np.ndarray = parent_tf[0]
                rot:Rotation = parent_tf[1]
            else:
                h5_key = pose_data['key']
                if h5_key[0] == '/':
                    pose:h5py.Group = self.h5file[h5_key]
                else:
                    pose:h5py.Group = h5data[h5_key]
                tr_tmp:np.ndarray = pose[SUBTYPE_TRANSLATION][()]
                rot_tmp:Rotation = Rotation.from_quat(pose[SUBTYPE_ROTATION][()])
                tr:np.ndarray = parent_tf[1].apply(tr_tmp) + parent_tf[0]
                rot:Rotation = parent_tf[1] * rot_tmp
            
            self.__draw_tf(config, key, (tr, rot), parent_tf)

            for child_key, child_item in children.items():
                draw_nest_tf(child_key, child_item, config, (tr, rot))

        config['widget'].clear()
        item = GLGridItem()
        item.setSize(200, 200)
        item.setSpacing(10, 10)
        config['widget'].addItem(item)

        if h5data.attrs.get(H5_ATTR_TYPE) == TYPE_POSE:
            self.__draw_tf(config, h5data.attrs[H5_ATTR_FRAMEID])
            self.__draw_tf(config, h5data.attrs[H5_ATTR_CHILDFRAMEID], (h5data[SUBTYPE_TRANSLATION][()], Rotation.from_quat(h5data[SUBTYPE_ROTATION][()])))
        else:
            for root_key, root_children in self.tf_tree_dict.items():
                draw_nest_tf(root_key, root_children, config)

def convert_str(obj:Any) -> str:
    if isinstance(obj, bytes) is True:
        return obj.decode()
    elif isinstance(obj, str) is True:
        return obj
    else:
        return str(obj)

def main():
    app = QApplication(sys.argv)
    h5v = H5DataViewer(app)
    h5v.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()