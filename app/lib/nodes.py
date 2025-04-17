import cv2

from typing import Tuple
from abc import ABC, abstractmethod
from lib.video_manager import VideoManager
from streamlit_flow.elements import StreamlitFlowNode


class Node:
    def __init__(self, id: str, pos: Tuple[float, float], node_type: str, source_position: str, target_position: str, data):
        self.id = id
        self.pos = pos
        self.node_type = node_type
        self.source_position = source_position
        self.target_position = target_position
        self.data = data
        self.node = self.build_node()  # Calling the node's build method

    def build_node(self):
        # Method to be implemented in subclasses
        pass
    

class InputNode(Node):
    def __init__(self, id, pos, data):
        super().__init__(id, pos, 'input', 'right', 'left', data['content'])
        self.video_manager = VideoManager(data['source_type'], data['source'])

    def initialize_video(self):
        """Initialize the video source"""
        self.video_manager.initialize()

    def get_frame(self):
        """Get the current video frame"""
        return self.video_manager.get_frame()
    
    def release(self):
        """Release the video"""
        return self.video_manager.release()

    def build_node(self):
        print("Building node with data:", self.data)
        node = StreamlitFlowNode(
            id=self.id,
            pos=self.pos,
            node_type=self.node_type,
            source_position=self.source_position,
            target_position=self.target_position,
            data={'content': self.data},
            connectable=True,
            deletable=True,
            draggable=True,
        )
        return node


class AssemblyStepNode(Node):
    def __init__(self, id: str, pos: Tuple[float, float], node_type: str, source_position: str, target_position: str, data):
        self.id = id
        self.pos = pos
        self.node_type = node_type
        self.source_position = source_position
        self.target_position = target_position
        self.data = data
        self.node = self.build_node()

        self.match: bool = False
        self.recognized: bool = False
        self.template_img_path = None
        self.template_img = None
        self.instruction_img_path = None
        self.instruction_img = None
        self.instruction_text = None
        self.obj_cls = None
        self.obj_idx = None
        self.obj_match_conf = None
        

    def build_node(self):
        print("Building node with data:", self.data)
        node = StreamlitFlowNode(
            id=self.id,
            pos=self.pos,
            node_type=self.node_type,
            source_position=self.source_position,
            target_position=self.target_position,
            data=self.data,
            connectable=True,
            deletable=True,
            draggable=True,
        )
        return node


class TaskNode(Node, ABC):
    def __init__(self, id, pos, data):
        super().__init__(id, pos, 'default', 'right', 'left', data)

    def build_node(self):
        print("Building node with data:", self.data)
        node = StreamlitFlowNode(
            id=self.id,
            pos=self.pos,
            node_type=self.node_type,
            source_position=self.source_position,
            target_position=self.target_position,
            data=self.data,
            connectable=True,
            deletable=True,
            draggable=True,
        )
        return node
    
    @abstractmethod
    def process_task(self):
        pass


class SquareTaskNode(TaskNode):
    
    def process_task(self, frame):
        # Desenhar um quadrado vermelho no centro
        height, width, _ = frame.shape
        center = (width // 2, height // 2)
        
        # Definir o tamanho do quadrado e a cor
        square_size = 100  # Tamanho de metade do lado do quadrado
        color = (0, 0, 255)  # Vermelho (BGR)
        thickness = 2  # Espessura da linha
        
        # Calcular os pontos superior esquerdo e inferior direito do quadrado
        top_left = (center[0] - square_size, center[1] - square_size)
        bottom_right = (center[0] + square_size, center[1] + square_size)
        
        # Desenhar o quadrado no frame
        frame_with_square = cv2.rectangle(frame, top_left, bottom_right, color, thickness)
        
        return frame_with_square
    

class OutputNode(Node):
    def __init__(self, id, pos, data):
        super().__init__(id, pos, 'output', 'left', 'left', data)


    def build_node(self):
        print("Building output node with data:", self.data)
        node = StreamlitFlowNode(
            id=self.id,
            pos=self.pos,
            node_type=self.node_type,
            source_position=self.source_position,
            target_position=self.target_position,
            data=self.data,
            connectable=True,
            deletable=True,
            draggable=True,
        )
        return node