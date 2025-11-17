import json

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition

from ..tools.functionTools import *


@AgentServer.custom_recognition("ZhuoGuiTask")
class ZhuoGuiTask(CustomRecognition):

    def analyze(
            self,
            context: Context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        param = json.loads(argv.custom_recognition_param)
        current_node = param.get("current_node")
        print(f"[捉鬼任务] 主界面")

        while True:
            # 获取最新画面
            if templateMatching(context, image(context), ["base/image/场景/主界面"]):
                print("[捉鬼任务] 已确认在主界面")
                break
            print("[捉鬼任务] 主界面识别失败，开始检测并处理弹窗")
            popup(context)
            print("[捉鬼任务] 重新检测主界面...")

        # # === 检查组队状态 ===
        # """打开组队界面"""
        # open_team_interface_ZhuoGui(context)
        # """队伍管理主流程"""
        # team_management(context)
        # # 检查任务栏有没有捉鬼任务，当前是否处于捉鬼战斗中
        # check_zhuogui_task(context)
        # === Step 3: 主循环：战斗检测 + 队伍管理 ===
        max_rounds = 15
        count = 0
        while_count = 0
        last_team_manage_time = time.time()
        TEAM_MANAGE_INTERVAL = 300

        # 用列表包装时间戳，便于在函数中更新
        last_team_time_ref = [last_team_manage_time]

        while count < max_rounds:
            while_count += 1
            # === 队伍管理条件判断（自动）===
            should_manage_team = False
            if while_count == 1:
                should_manage_team = True
                print("[捉鬼任务] 第一轮，强制执行队伍管理")
            # elif TEAM_MANAGE_INTERVAL > 0 and (time.time() - last_team_manage_time >= TEAM_MANAGE_INTERVAL):
            #     should_manage_team = True
            #     print("[捉鬼任务] 距离上次队伍管理已超300秒，执行队伍管理")

            if should_manage_team:
                perform_team_management(context, last_team_time_ref)
            print(f"[捉鬼任务] 第 {count + 1} 轮检测...")
            # === 捉鬼状态检测 ===
            state, count = check_zhuogui_task(context, count)

            if state == ZhuoGuiState.ROUND_COMPLETED:
                print(f"✅ 已完成 {count} 轮")
                # 注意：这里不需要 sleep(90)，因为“继续捉鬼”弹窗刚点完，应尽快进入下一轮
                time.sleep(3)  # 短暂等待界面刷新
                # 检查到达钟馗场景
                templateMatching(context, image(context), "捉鬼任务/钟馗场景.png")
                # 领取任务
                identify_and_click(context, "捉鬼任务/开启捉鬼任务.png")

                identify_and_click(context, "捉鬼任务/领取抓鬼任务成功.png")

            elif state == ZhuoGuiState.IN_BATTLE:
                # print("[捉鬼任务] 检测到战斗，等待135秒...")
                # time.sleep(135)
                print("[捉鬼任务] 检测到战斗，等待135秒...")
                wait_time = 135

                for i in range(wait_time, 0, -1):
                    print(f"\r剩余等待时间: {i}秒", end="", flush=True)
                    time.sleep(1)

            elif state == ZhuoGuiState.NEED_TEAM:
                # 👇 立即触发队伍管理
                perform_team_management(context, last_team_time_ref)
                time.sleep(0.5)  # 等待队伍操作生效
            context.override_next(current_node, next_list=["结束"])
        return CustomRecognition.AnalyzeResult(box=[0, 0, 0, 0], detail="")
