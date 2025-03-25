import random
import time
import re
from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import astrbot.api.message_components as Comp

# 关键词列表
keywords = ["攻击", "猛攻", "戳"]
# 冷却话术列表
cooling_down_messages = [
    "人家戳到手疼了，晚点再玩嘛。",
    "让我歇会儿，等下再戳。",
    "我累啦，过会儿再继续。"
]
# 不能自己戳自己的话术列表
self_poke_messages = [
    "让你戳了吗",
    "别让我自己戳自己啦，很奇怪的。",
    "我才不要自己戳自己呢。"
]
# 收到指令的回复话术列表
received_commands_messages = [
    "收到指令，马上发动戳一戳攻击！",
    "指令已接收，准备出击！",
    "好嘞，这就去戳戳Ta！",
    "收到收到！"
]

@register("PockAttack", "Louie", "戳一戳攻击插件", "1.0.0", "https://github.com/yourrepo")
class PokeAttack(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.cooling_down = False
        self.cooling_end_time = 0

    @event_message_type(EventMessageType.GROUP_MESSAGE)
    async def handle_group_message(self, event: AstrMessageEvent):
        message_obj = event.message_obj # 获取消息对象
        message_str = message_obj.message_str # 消息文本内容
        self_id = event.get_self_id() # 机器人QQ号
        group_id = message_obj.group_id # 群号

        # 检查消息开头是否有关键词
        for keyword in keywords:
            if message_str.startswith(keyword):
                
                # 确定戳一戳的次数 (有感叹号会触发更多戳戳)
                if re.match(rf'^{keyword}(！|!)$', message_str):
                        poke_times = random.randint(5, 10)
                else:
                    poke_times = random.randint(1, 3)

                # 提取消息中 @ 的用户
                messages = event.get_messages()
                target_user_id = next((str(seg.qq) for seg in messages if (isinstance(seg, Comp.At))), None)

                # 检查是否有 @ 的用户
                if target_user_id is None:
                    return
                # 检查受击人是否机器人本体
                if str(target_user_id) == str(self_id):
                    yield event.plain_result(random.choice(self_poke_messages)) # self_poke_messages 为不能自己戳自己的话术列表
                    return
                
                # 检查是否在冷却期
                if self.cooling_down and time.time() < self.cooling_end_time:
                    yield event.plain_result(random.choice(cooling_down_messages))
                    return
                
                # 攻击前自嗨
                yield event.plain_result(random.choice(received_commands_messages))

                # 发送戳一戳
                payloads = {"user_id": target_user_id, "group_id": group_id}
                for _ in range(poke_times):
                    try:
                        await event.bot.api.call_action('send_poke', **payloads)
                    except Exception as e:
                        pass

                # 进入冷却期
                self.cooling_down = True
                cooling_duration = random.randint(30, 60)
                self.cooling_end_time = time.time() + cooling_duration
                return

    
