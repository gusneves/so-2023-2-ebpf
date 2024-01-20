#!/usr/bin/python
from bcc import BPF

# Aqui é descrito o nosso programa eBPF (em C), 
# que será executado diretamente no kernel.
#
# Com o auxílio da biblioteca bcc
# conseguimos definir, compilar e executar o programa 
# em um único arquivo .py
program = """
int hello_world(void *ctx){
    bpf_trace_printk("Hello, World!\\n");
    return 0;
}
"""

# Carregamos o programa descrito acima em um novo módulo BPF
b = BPF(text=program)

# A partir do módulo BPF, pegamos o nome da função atribuída a uma syscall
# Exemplo: "clone" retorna "sys_clone"
clone = b.get_syscall_fnname("clone")

# Instrumenta a função do kernel `event` 
# e atrela a ela a função `name` a esse evento.
#
# Nesse caso, toda vez que o evento `sys_clone` for chamado
# nossa função BPF `hello_world` será executada
b.attach_kprobe(event=clone, fn_name="hello_world")
try:
    # Este método lê o arquivo globalmente compartilhado*
    # /sys/kernel/debug/tracing/trace_pipe
    #
    # (*) Problemas de concorrência
    b.trace_print()
except KeyboardInterrupt:
    exit()