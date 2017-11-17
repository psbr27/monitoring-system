from collections import defaultdict
from string import Template

import logmanager

log_m = logmanager.LogManager()
log = log_m.logger()


class PyGen:
    def __init__(self):
        self.code = open("code_gen.py", "a+")
        self.tab = "    "
        self.level = 0

    def end(self):
        self.code.close()

    def write(self, string):
        # self.code.append(self.tab * self.level + string + "\n")
        self.code.write(self.tab * self.level + string + "\n")

    def newline(self, no=1):
        res = ""
        i = 1
        while (i <= no):
            res += "\n"
            i += 1
        # self.code.append(res)heart_beat_dict =
        self.code.write(res)

    def indent(self):
        self.level = self.level + 1

    def dedent(self):
        if self.level == 0:
            raise SyntaxError, "internal error in code generator"
        self.level = self.level - 1


d = defaultdict(int)


def create_dictionary(c, esc_list):
    s = Template("heart_beat_dict = {$hb_dict}")

    for item in esc_list:
        d[item] += 0

    c.write(s.substitute(hb_dict=d.items()))
    c.newline(4)


def construct_import(c):
    c.write("import Queue")
    c.write("import threading")
    c.write("import time")
    c.write("import snmp_stat as snmp")
    c.write("import trap_v2c as snmp_trap")
    c.write("import logmanager")
    c.write("log_m = logmanager.LogManager()")
    c.write("log = log_m.logger()")
    c.write("heart_beat_counter = 0")
    c.write("count = 0")
    c.write("thread_list = []")


# doesn't grow or shrink
def create_queue_put_handler(c, esc):
    # add a comment
    c.write("#=====o======o=====o======o=====o======o=====o======o=====")
    c.write("def put_data_into_queue(username, data):")
    c.indent()
    c.write("get_idx = username[8:12]")
    c.write("esc_q = 'esc_sn' + get_idx + '_Q'")
    c.write("esc_q.put(data)")
    c.dedent()
    c.newline(no=4)


# doesn't grow or shrink
def create_esc_thread_handler(c):
    # add a comment to the beginning of the function
    c.write("#=====o======o=====o======o=====o======o=====o======o=====")
    c.write("def esc_thread_handler(username):")
    c.indent()
    c.write("if username in esc_list:")
    c.indent()
    c.write('q_thread = username + "__q_thread"')
    c.write('esc_worker = threading.Thread(name=username, target=q_thread, args=(username,))')
    c.write("esc_worker.setDaemon = True")
    c.write("esc_worker.start()")
    c.dedent()
    c.dedent()
    c.newline(no=4)


# Grows ++
def generate_code(c, esc):
    c.write("#=====o======o=====o======o=====o======o=====o======o=====")
    username = esc + "_handler"
    s = Template('def $escName(username, entry, esc_id, op_state, location, admin_state):')
    c.write(s.substitute(escName=username))
    c.indent()

    queue_name = esc + "_Q"
    s = Template('if $queueName.empty():')

    c.write(s.substitute(queueName=queue_name))
    c.indent()
    c.write("heart_beat_counter = heart_beat_dict[username]")
    c.write("if heart_beat_counter == 3:")
    c.indent()
    c.write("log.warn('No heart beat detected for $$, raise a trap')")
    c.write("snmp.snmp_set_operations(esc_id, op_state, location, entry, admin_state)")
    c.write("snmp_trap.trigger_trap('No heartbeat detected')")
    c.write("heart_beat_dict[username] = 0")
    c.dedent()
    c.write("else:")
    c.indent()
    c.write("heart_beat_counter = heart_beat_counter + 1")
    c.write("heart_beat_dict[username] = heart_beat_counter")
    c.dedent()
    c.dedent()
    c.write("else:")
    c.indent()
    s = Template('$queueName.get(True, 15)')
    c.write(s.substitute(queueName=queue_name))
    c.write("snmp.snmp_set_operations(esc_id, op_state, location, entry, admin_state)")
    s = Template('$queueName.task_done()')
    c.write(s.substitute(queueName=queue_name))

    c.newline(no=2)  # adding 4 new lines
    c.dedent()
    c.dedent()

    queue_thread = esc + "__q_thread"
    s = Template('def $queueThread(username):')
    c.write("#=====o======o=====o======o=====o======o=====o======o=====")
    c.write(s.substitute(queueThread=queue_thread))
    c.indent()
    c.write("thread_list.append(username)")
    c.write("while True:")
    c.indent()
    s = Template('t = threading.Timer(15.0, $escName, args=(username,))')
    c.write(s.substitute(escName=username))
    c.write('t.start()')
    c.write('time.sleep(15)')
    c.dedent()
    c.dedent()
    c.write("#=====o======o=====o======o=====o======o=====o======o=====")
    c.newline(no=2)


# if __name__ == '__main__':
def invoke_code_generator(esc_list):
    log.info("++++ Code generation begins ++++")
    c = PyGen()
    construct_import(c)
    for item in esc_list:
        s = Template("$esc_q = Queue.Queue(100)")
        c.write(s.substitute(esc_q=item + "_Q"))
    create_dictionary(c, esc_list)
    create_queue_put_handler(c, "fed_esc_014")
    create_esc_thread_handler(c)
    for item in esc_list:
        generate_code(c, item)
    c.end()
    log.info("++++ Code generation end ++++")
