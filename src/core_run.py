from core.RaspiFM import RaspiFM
from core.socket.MessageManager import MessageManager

raspifm = RaspiFM()
MessageManager.handle_messages(raspifm)