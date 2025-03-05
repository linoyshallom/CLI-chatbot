import enum
import typing


class RoomTypes(enum.Enum):
    GLOBAL = "GLOBAL"
    PRIVATE = "PRIVATE"
    # DIRECT = "DIRECT"


# a: typing.Dict[RoomTypes,str] = {}
# a[RoomTypes.GLOBAL]= "g"
# for x in RoomTypes:
#     print(x)
#     # print(type(x))
# print(a)
# print(type(RoomTypes["GLOBAL"]))
# print(a.get(RoomTypes["GLOBAL"]))