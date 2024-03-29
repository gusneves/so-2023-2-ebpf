# so-2023-2-ebpf

---

## eBPF: Programando o Kernel

Equipe: SOIA

Participantes:

- 202107016 - Gustavo Neves Piedade Louzada
- 202107018 - Hafy Mourad Jacoub de Cuba Kouzak
- 202107021 - Igor Rodrigues Castilho
- 202107023 - João Victor de Paiva Albuquerque
- 202108922 - Maria Eduarda de Campos Ramos

### Seções

- [Introdução](#introdução)
- [Fundamentos Teóricos](#fundamentos-teóricos)
- [Metodologia](#metodologia)
- [Resultados e Conclusões](resultados-e-conclusões)
- [Referências](#referências)
- [Apêndice A](apêndice-a)

### Introdução

Originária de uma evolução do BPF (_Berkeley Packet Filter_), o eBPF (acrônimo para _Extended Berkeley Packet Filter_) é uma tecnologia que permite a execução de programas no contexto privilegiado do kernel do sistema operacional de maneira segura e eficiente, podendo estender as capacidades do kernel, sem a necessidade de modificá-lo ou carregar módulos.

Devido à habilidade privilegiada do kernel para supervisionar e controlar todo o sistema, o sistema operacional é o local ideal para a implementação de funcionalidades de observabilidade, segurança e rede. No entanto, devido ao papel central do kernel e seus altos requisitos de segurança e estabilidade, alterar e evoluir seu comportamento torna-se uma tarefa complexa e demorada, atrasando a taxa de inovação em comparação com as funcionalidades fora do escopo do sistema operacional.

O eBPF altera essa lógica, de modo que permite a execução de programas isolados dentro do sistema operacional, permitindo a adição de capacidades adicionais em tempo de execução, sendo a segurança e a eficiência desta execução garantidas pelo próprio sistema operacional com o auxílio de um compilador _Just-In-Time_ (JIT) e um mecanismo de verificação (eBPF Documentation).

Suas aplicações atuais abrangem áreas como monitoramento de rede, instrumentação do kernel, segurança, otimização de desempenho, análise de sistema, observabilidade, ferramentas de desenvolvimento e extensões de sistema de arquivos. Sua versatilidade tornou-o uma ferramenta poderosa para melhorar a observabilidade, segurança e desempenho em ambientes de produção, sendo amplamente adotado em uma variedade de cenários, desde análise de pacotes de rede até o desenvolvimento de ferramentas avançadas de observabilidade e segurança em sistemas Linux.

### Fundamentos teóricos

Os programas eBPF constituem uma tecnologia baseada em eventos, operando quando o kernel ou um aplicativo atinge um ponto de ancoragem específico, conhecido como "_hook_". Esses pontos de ancoragem abrangem diversas categorias, como chamadas do sistema, funções de entrada e saída, rastreamento do kernel, eventos de rede, entre outros.

Na ausência de um gancho predefinido para uma necessidade específica, é possível criar um "_kernel probe_" (kprobe) ou "_user probe_" (uprobe). Isso permite a vinculação de programas eBPF virtualmente em qualquer parte do kernel ou em aplicações de usuário.

Em muitos cenários, a utilização direta de eBPF não é necessária. Projetos como Cilium, bcc e bpftrace oferecem abstrações sobre o eBPF, permitindo a definição de intenções sem a necessidade de escrever programas diretamente. Essas abstrações simplificam o desenvolvimento, proporcionando uma interface mais amigável.

Caso não haja uma abstração disponível, os programas eBPF precisam ser escritos diretamente. O kernel Linux espera que esses programas sejam carregados na forma de bytecode. Embora seja possível escrever bytecode manualmente, a prática comum envolve o uso de suítes de compiladores, como o LLVM, para converter código pseudo-C em bytecode eBPF.

O carregamento efetivo do programa eBPF no kernel Linux é realizado por meio da chamada de sistema bpf. Normalmente, bibliotecas específicas para eBPF facilitam esse processo, simplificando a interação do desenvolvedor com o kernel.
Antes de serem anexados ao gancho desejado, os programas eBPF passam por duas etapas críticas: Verificação e Compilação JIT. Essas etapas críticas garantem a segurança e a eficiência dos programas eBPF durante seu ciclo de vida no kernel Linux.

A etapa de verificação assegura a segurança do programa eBPF antes da execução. Diversas condições são validadas, incluindo a posse de privilégios necessários pelo processo que carrega o programa eBPF. Esta etapa garante que o programa não cause falhas no sistema e seja executado até o final, evitando loops infinitos que prejudiquem o processamento adicional.

A etapa JIT traduz o bytecode genérico do programa para um conjunto de instruções específico da máquina. Isso otimiza a velocidade de execução do programa eBPF, garantindo eficiência comparável ao código nativo do kernel ou a módulos de kernel carregados.

Uma característica fundamental dos programas eBPF é sua capacidade de compartilhar informações coletadas e manter o estado ao longo do tempo. Para este fim, os programas eBPF utilizam o conceito de "mapas eBPF", permitindo o armazenamento e a recuperação eficiente de dados em diversas estruturas de dados. Esses mapas podem ser acessados não apenas por outros programas eBPF, mas também por aplicativos no espaço do usuário, possibilitando uma comunicação efetiva por meio de chamadas de sistema. Exemplo de mapas suportados: tabelas de hash, matrizes, buffer circular, rastreamento de pilha, entre outros.

É crucial notar que os programas eBPF não têm a capacidade de chamar funções do kernel arbitrariamente. Tal permissão vincularia esses programas a versões específicas do kernel, complicando a compatibilidade e a manutenção dos programas. Em vez disso, os programas eBPF podem realizar chamadas de função para as chamadas de assistência, constituindo uma API estável e bem conhecida fornecida pelo kernel. Exemplos de chamadas de assistência disponíveis: gerar números aleatórios, obter data e hora atuais, obter contexto de processo, manipular pacotes de rede e lógica de encaminhamento.

Os programas eBPF são projetados com um foco na composabilidade, introduzindo os conceitos de "chamadas de cauda" (tail calls) e funções. As chamadas de função permitem a definição e execução de funções dentro de um programa eBPF, facilitando a modularização do código. Por outro lado, as chamadas de cauda possibilitam a execução de outro programa eBPF, substituindo o contexto de execução. Esse comportamento é análogo à chamada de sistema execve() para processos regulares, proporcionando uma flexibilidade notável na execução e na estruturação dos programas eBPF.

Essas características expandem significativamente o escopo e a utilidade dos programas eBPF, tornando-os não apenas poderosos em termos de rastreamento e filtragem, mas também altamente flexíveis e adaptáveis a uma variedade de cenários de uso. A seção subsequente discute uma das aplicações práticas dessas capacidades, destacando um caso de uso comum e implementação exemplar.

### Metodologia

A fim de expandir o comportamento do kernel de maneira segura, eficiente e rápida, e demonstrar a instrumentalização deste através do eBPF, utilizaremos as funcionalidades do toolkit open source BPF Compiler Collection (BCC).

Dentre as funcionalidades do BCC, encontramos umwrapper da linguagem C, que permite a declaração do móduloBPF, que será executado diretamente no kernel. Com isto, conseguimos, em um único arquivo, codificar os programas que serão executados no kernel space e no user space.

No algoritmo 1, codificamos o módulo BPF que será executado no kernel, abrangendo as linhas 1 a 22. Nele, definimos um tipo data_t que será utilizado para armazenar as informações de um processo, como seu nome, PID, o timestamp de sua criação e o ID do usuário que o criou. Na linha 9, utilizamos a função BPF_PERF_OUTPUT, que inicializa um buffer circular que servirá como meio de comunicação e compartilhamento de dados entre o programa eBPF e o programa rodando no user space.

A função register_event, definida das linhas 11 a 20, será responsável por pegar os dados dos processos, atribuí-los a uma estrutura do tipo definido anteriormente e registrá-los no buffer events. Na linha 22, é criado um objeto BPF, responsável por definir o programa BPF (no caso, o programa em C previamente codificado) e interagir com sua saída (bcc Reference Guide).
Após a definição do programa BPF, é necessário instrumentalizar uma função do kernel e anexar a função em C para ser executada toda vez que a chamada de sistema escolhida ocorrer, assim como mostra o algoritmo 2.

Dessa maneira, toda vez que a chamada de sistema “clone”, cujo nome da função é “sys_clone” e é responsável pela criação de um novo processo, é acionada, a função register_event será executada e armazenará os dados do novo processo que foi iniciado no buffer events.

No algoritmo 3, é definida a função print_event, que será responsável por imprimir, de maneira formatada, os eventos submetidos ao buffer. Na linha 36, abrimos para o programa do user space o acesso ao buffer e anexamos a função como callback, de modo que ela seja executada para cada evento submetido, mas apenas após a chamada da função perf_buffer_poll, que capta as entradas de todos os perf buffers abertos.

Para mais detalhes sobre a implementação, o código completo está disponibilizado no Apêndice A.

### Resultados e Conclusões

Podemos observar na Figura 3, a saída do programa descrito, onde é possível rastrear os processos que foram iniciados, bem como seus respectivos identificadores e os usuários responsáveis por sua criação, associados a um instante no tempo.

Tal comportamento, não implementado no kernel por padrão, poderia ter muita utilidade, por exemplo, em um cenário de um servidor acessado por inúmeros usuários, já que permite, com eficiência, a rastreabilidade dos processos executados no servidor.

Portanto, conclui-se que, a partir da metodologia utilizada, foi possível verificar a utilidade do eBPF na prática. O código implementou uma funcionalidade nova no kernel, que não existe por padrão, de forma rápida, eficiente e segura. Tal atualização de comportamento, seguindo meios mais tradicionais, poderia se tornar uma tarefa extremamente custosa e complexa.

### Referências

- EBPF Documentation. [S. l.], 2020. Disponível em: https://ebpf.io/what-is-ebpf/. Acesso em: 14 jan. 2024.
- EBPF: Unlocking the Kernel [OFFICIAL DOCUMENTARY]. Produção: Speakeasy Productions. [S. l.: s. n.], 2023. Disponível em: https://www.youtube.com/watch?v=Wb_vD3XZYOA. Acesso em: 14 jan. 2024.
- VIZARD, MIKE. Foundation Proposes Advancing eBPF Adoption Across Multiple OSes. Flórida, Estados Unidos, 12 ago. 2021. Disponível em: https://devops.com/foundation-proposes-advancing-ebpf-adoption-across-multiple-oses/. Acesso em: 14 jan. 2024.
- BCC Reference Guide. GitHub: IO Visor Project, 26 jul. 2016. Disponível em: https://github.com/iovisor/bcc/blob/master/docs/reference_guide.md. Acesso em: 21 jan. 2024.

### Apêndice A

```
1 #!/usr/bin/python
2 from bcc import BPF
3 from bcc.utils import printb
4
5 # Utilização da BPF_PERF_OUTPUT
6 # Cria uma tabela BPF para enviar dados
customizados de eventos para o user space
7 # via perf ring buffer
8 program = """
9 #include <linux/sched.h>
10 struct data_t {
11 u32 uid;
12 u32 pid;
13 u64 ts;
14 char comm[TASK_COMM_LEN];
15 };
16
17 BPF_PERF_OUTPUT(events);
18
19 int register_event(void *ctx){
20 struct data_t data = {};
21 data.uid = bpf_get_current_uid_gid() >> 32;
22 data.pid = bpf_get_current_pid_tgid();
23 data.ts = bpf_ktime_get_ns();
24 bpf_get_current_comm(&data.comm,
sizeof(data.comm));
25
26 events.perf_submit(ctx,&data,
27 sizeof(data));
28 return 0;
29 }
30 """
31
32 b = BPF(text=program)
33 clone = b.get_syscall_fnname("clone")
34 b.attach_kprobe(event=clone,
fn_name="register_event")
35 # header da tabela
36 print("%-18s %-16s %-6s %-6s %s" %
("TIME(s)", "COMM","PID", "UID", "MESSAGE"))
37
38 # Processamento dos eventos
39 start = 0
40 def print_event(cpu, data, size):
41 global start
42 event = b["events"].event(data)
43 if start == 0:
44 start = event.ts
45 time_s = (float(event.ts - start)) /
1000000000
46 printb(b"%-18.9f %-16s %-6d %-6d %s" %
(time_s, event.comm, event.pid, event.uid,
47 b"Hello, perf_output!"))
48
49 # loop com callback para print_event
50 b["events"].open_perf_buffer(print_event)
51
52 while True:
53 try:
54 b.perf_buffer_poll()
55 except KeyboardInterrupt:
56 exit()
```
