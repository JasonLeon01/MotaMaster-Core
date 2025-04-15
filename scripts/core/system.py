import os
from configparser import ConfigParser
from typing import Any, Dict, List

from PySFBoost.sfSystem import Vector2f, Vector2u
from PySFBoost.sfWindow import ContextSettings, Style, VideoMode
from PySFBoost.sfGraphics import Color, Font, Image, RenderWindow
from PySFBoost.TextEnhance import EText
from PySFBoost.ResourceMgr import FontMgr, TextureMgr
from . import scene
from .method import load_json_file

data_cache = {}
if os.path.exists('data.mtpak'):
    import pickle
    with open('data.mtpak', 'rb') as f:
        data_cache = pickle.load(f)

assets_cache = {}
if os.path.exists('assets.mtpak'):
    import pickle
    with open('assets.mtpak', 'rb') as f:
        assets_cache = pickle.load(f)
    TextureMgr.add_pak_ref(assets_cache)

class System:
    window: RenderWindow = None
    _size = Vector2f(640, 480)
    _scale = 1
    _title = ''
    _font: List[Font] = []
    _font_size = 20
    _font_style_config: EText.StyleConfig = None
    _smooth = False
    _frame_rate = 30
    _vertical_sync = False
    _icon: Image = None
    is_music_on = True
    is_sound_on = True
    is_voice_on = True
    current_scene: scene.SceneBase = None
    _variables: Dict[str, Any] = {}

    @classmethod
    def init(cls, inifile):
        iniconfig = ConfigParser()
        iniconfig.read(inifile)
        cls._title = Config.title_name
        cls._scale = iniconfig['Mota'].getfloat('Scale')
        cls._frame_rate = iniconfig['Mota'].getint('FrameRate')
        cls._smooth = iniconfig['Mota'].getboolean('Smooth')
        cls._vertical_sync = iniconfig['Mota'].getboolean('VerticalSync')
        cls.is_music_on = iniconfig['Mota'].getboolean('MusicOn')
        cls.is_sound_on = iniconfig['Mota'].getboolean('SoundOn')
        cls.is_voice_on = iniconfig['Mota'].getboolean('VoiceOn')

        cls._real_size = (cls._size * cls._scale).to_uint()
        cls.current_scene = None
        context_settings = ContextSettings()
        context_settings.antiAliasingLevel = 8
        cls.window = RenderWindow(VideoMode(cls._real_size), cls._title, Style.Titlebar | Style.Close, settings=context_settings)
        ico_image = TextureMgr.system(Config.title_icon).copy_to_image()
        cls.window.set_icon(ico_image)
        TextureMgr.release_system(Config.title_icon)
        cls.window.set_framerate_limit(cls._frame_rate)
        cls.window.set_vertical_sync_enabled(cls._vertical_sync)
        cls.window.clear(Color.black())
        cls.window.display()

        cls._font = []
        for font in Config.font_name:
            font_ = FontMgr.get_font_from_file(font)
            font_.set_smooth(cls._smooth)
            cls._font.append(font_)
        cls._font_style_config = EText.StyleConfig(Color.white(), cls._font_size, 1.0, 1.0)

        print('System initialized successfully.')

    @classmethod
    def get_size(cls) -> Vector2f:
        return cls._size

    @classmethod
    def get_real_size(cls) -> Vector2u:
        return cls._real_size

    @classmethod
    def get_scale(cls) -> float:
        return cls._scale

    @classmethod
    def set_scale(cls, scale: float):
        cls._scale = scale
        cls._real_size = (cls._size * cls._scale).to_uint()
        cls.window.set_size(cls._real_size)

    @classmethod
    def get_title(cls) -> str:
        return cls._title

    @classmethod
    def set_title(cls, title: str):
        cls._title = title
        cls.window.set_title(title)

    @classmethod
    def get_font(cls) -> List[Font]:
        return cls._font

    @classmethod
    def get_frame_rate(cls) -> int:
        return cls._frame_rate

    @classmethod
    def set_frame_rate(cls, frame_rate: int):
        cls._frame_rate = frame_rate
        cls.window.set_framerate_limit(frame_rate)

    @classmethod
    def get_smooth(cls) -> bool:
        return cls._smooth

    @classmethod
    def get_vertical_sync(cls) -> bool:
        return cls._vertical_sync

    @classmethod
    def set_vertical_sync(cls, vertical_sync: bool):
        cls._vertical_sync = vertical_sync
        cls.window.set_vertical_sync_enabled(vertical_sync)

    @classmethod
    def get_font_style_config(cls) -> EText.StyleConfig:
        return cls._font_style_config

    @classmethod
    def set_font_style_config(cls, font_style_config: EText.StyleConfig):
        cls._font_style_config = font_style_config

    @classmethod
    def set_variable(cls, name, value):
        cls._variables[name] = value

    @classmethod
    def get_variable(cls, name):
        if name in cls._variables:
            return cls._variables[name]
        return 0

class Config:
    title_name: str
    title_icon: str
    title_file: str
    title_bgm: str
    font_name: List[str]
    font_size: int
    windowskin_file: str
    window_opacity: int

    cursor_se: str
    decision_se: str
    cancel_se: str
    buzzer_se: str
    shop_se: str
    save_se: str
    load_se: str
    gate_se: str
    stair_se: str
    get_se: str

    @classmethod
    def init(cls, files):
        if os.path.exists(files[0]):
            config_sys = load_json_file(files[0])
        else:
            path_parts = files[0].replace('\\', '/').split('/')
            config_type = path_parts[-2]
            config_name = path_parts[-1].split('.')[0]
            config_sys = data_cache[config_type][config_name]

        cls.title_name = config_sys['title_name']
        cls.title_icon = config_sys['title_icon']
        cls.title_file = config_sys['title_file']
        cls.title_bgm = config_sys['title_bgm']
        cls.font_name = config_sys['font_name']
        cls.font_size = config_sys['font_size']
        cls.windowskin_file = config_sys['windowskin_file']
        cls.window_opacity = config_sys['window_opacity']

        if os.path.exists(files[1]):
            config_audio = load_json_file(files[1])
        else:
            path_parts = files[1].replace('\\', '/').split('/')
            config_type = path_parts[-2]
            config_name = path_parts[-1].split('.')[0]
            config_audio = data_cache[config_type][config_name]
        cls.cursor_se = config_audio['cursor_se']
        cls.decision_se = config_audio['decision_se']
        cls.cancel_se = config_audio['cancel_se']
        cls.buzzer_se = config_audio['buzzer_se']
        cls.shop_se = config_audio['shop_se']
        cls.save_se = config_audio['save_se']
        cls.load_se = config_audio['load_se']
        cls.gate_se = config_audio['gate_se']
        cls.stair_se = config_audio['stair_se']
        cls.get_se = config_audio['get_se']

        print('Config initialized successfully.')
