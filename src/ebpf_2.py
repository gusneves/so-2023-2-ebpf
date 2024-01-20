#!/usr/bin/python
from time import sleep
from bcc import BPF

# Programa com a utilização de um hash map
# compartilhado entre o módulo BPF e o programa no user space.
# Utilização da estrutura de dados ao invés do pipe global.
#
# Conta o número de processos iniciados por cada usuário
program = """
#include <uapi/linux/ptrace.h>
BPF_HASH(clones);

int counter(void *ctx){
    u64 uid;
    u64 counter = 0;
    u64 *p;

    uid = bpf_get_current_uid_gid() >> 32;

    p = clones.lookup(&uid); 
    if(p != 0){
        counter = *p;
    }

    counter++;
    clones.update(&uid, &counter);

    return 0;
}
"""
# Mesmo processo do programa anterior
b = BPF(text=program)
clone = b.get_syscall_fnname("clone")
b.attach_kprobe(event=clone, fn_name="counter")

# Loop para leitura do hash map
try:
    while True:
        sleep(2)
        s = ""
        if len(b["clones"].items()):
            for k, v in b["clones"].items():
                s += "ID {}: {}\t".format(k.value, v.value)
            print(s)
        else:
            print("No entries yet")
except KeyboardInterrupt:
    exit()

