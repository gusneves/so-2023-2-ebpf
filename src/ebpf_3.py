#!/usr/bin/python
from bcc import BPF
from bcc.utils import printb

# Utilização da BPF_PERF_OUTPUT
# Cria uma tabela BPF para enviar dados customizados de eventos para o user space
# via perf ring buffer
program = """
#include <linux/sched.h>
struct data_t {
    u32 uid;
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(events);

int register_event(void *ctx){
    struct data_t data = {};

    data.uid = bpf_get_current_uid_gid() >> 32;
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
"""

b = BPF(text=program)
clone = b.get_syscall_fnname("clone")
b.attach_kprobe(event=clone, fn_name="register_event")
# header da tabela
print("%-18s %-16s %-6s %-6s %s" % ("TIME(s)", "COMM","PID", "UID", "MESSAGE"))

# Processamento dos eventos
start = 0
def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    if start == 0:
            start = event.ts
    time_s = (float(event.ts - start)) / 1000000000
    printb(b"%-18.9f %-16s %-6d %-6d %s" % (time_s, event.comm, event.pid, event.uid,
        b"Hello, perf_output!"))

# loop com callback para print_event
b["events"].open_perf_buffer(print_event)

while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()

