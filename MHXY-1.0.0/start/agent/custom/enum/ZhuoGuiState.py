from enum import Enum


class ZhuoGuiState(Enum):
    IN_BATTLE = "捉鬼中"
    ROUND_COMPLETED = "已完成一轮捉鬼"
    NEED_TEAM = "需要组队参与捉鬼任务"
    IDLE = "idle"
