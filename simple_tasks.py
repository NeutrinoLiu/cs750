from tasks import Res, Task

# def gen_simple():
#     r0 = Res(0, 5)
#     r1 = Res(1, 5)
#     r2 = Res(2, 5)
#     r3 = Res(3, 5)
#     t0 = Task(
#         0,
#         [r0],
#         [(None,1), (r0,5), (None,1)],
#         40,
#         40
#     )
#     t1 = Task(
#         1,
#         [r1, r2],
#         [(None,1), (r1,5), (None,1), (r2,5), (None,1)],
#         60,
#         60
#     )
#     t2 = Task(
#         2,
#         [r1, r3],
#         [(None,4), (r1,5), (None,1), (r3,5), (None,1)],
#         80,
#         80
#     )
#     t3 = Task(
#         3,
#         [r3],
#         [(None,1), (r3,5), (None,1)],
#         30,
#         30
#     )
#     return [r0, r1, r2, r3], [t0, t1, t2, t3]

def gen_simple():
    r0 = Res(0, 8)
    t0 = Task(
        0,
        [],
        [(None,8)],
        32,
        32,
        8
    )
    t1 = Task(
        1,
        [r0],
        [(None,4), (r0,8), (None,4)],
        64,
        64
    )
    t2 = Task(
        2,
        [r0],
        [(None,4), (r0,8), (None,4)],
        96,
        96
    )

    return [r0], [t0, t1, t2]