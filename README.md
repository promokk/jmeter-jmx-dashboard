# Jmeter-jmx-dashboard
Дашборд Grafana для мониторинга JMX-метрик процесса Jmeter.  
Позволяет отслеживать утилизацию ресурсов Jmeter во время теста.  
Для работы дашборда используется Prometheus, [Jmx-exporter](https://github.com/prometheus/jmx_exporter)
и [Node-exporter](https://github.com/prometheus/node_exporter).

Дашборд загружен в [Grafana Labs](https://grafana.com/grafana/dashboards/22106-jmeter-jmx-dashboard/).

---
# Оглавление
* [Описание дашборда](#dashboardDescription)
  * [Summary](#summary)
  * [CPU / Memory](#cpuMemory)
  * [Heap / NonHeap](#heapNonHeap)
  * [Garbage Collection (GC)](#garbageCollection)
  * [Threads](#threads)
  * [Native Memory](#nativeMemory)
* [Настройка окружения](#settings)
  * [Prometheus и Node-exporter](#prometheusNodeExporter)
  * [Jmx-exporter](#jmxExporter)
  * [Jmeter](#jmeter)
  * [Запуск Jmeter в Non-GUI mode](#runJmeter)

---
## Описание дашборда <a id="dashboardDescription"></a>
Чтобы писать производительные скрипты, нужно понимать, сколько ресурсов потребляют разные вариации скриптов Jmeter.  
Данный дашборд поволяет отслеживать утилизацию Jmeter во время теста.  
Node-exporter работает на сервере постоянно. Он необходим для панелей CPU.  
Jmx-exporter запускается как java-agent при запуске Jmeter, следовательно, завершает свою работу по окончанию теста.

---
###  Summary <a id="summary"></a>
Базовая информация об утилизации процесса Jmeter в течение теста также содержит еще несколько полезных панелей.
* Утилизация CPU % / Memory %
* Утилизация Heap % / NonHeap %
* Количество классов, которые в данный момент загружены в приложении
* Версия JVM
* Start Time - начало записи . Дата кликабельна. Отображает период от начала записи до выбранной точки.
* Uptime - время от начала записи до выбранной точки.

![Summary - гифка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/Summary.gif)

---
### CPU / Memory <a id="cpuMemory"></a>
Информация об утилизации CPU и Memory.
* Утилизации CPU % / Memory %
* Утилизация CPU - утилизация CPU процессом / всего доступно (millicore)
* Memory - утилизация памяти процессом / общий объем памяти

![CPU / Memory - картинка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/CPU_Memory.png)

---
### Heap / NonHeap <a id="heapNonHeap"></a>
Информация об утилизации Heap (Куча) и NonHeap (Стэк).
* Утилизация Heap % / NonHeap %
* Утилизация Heap / NonHeap
  * USED - используемая память
  * COMMITTED - доступная память
  * MAX - максимальный размер памяти

![Heap / NonHeap - картинка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/Heap_NonHeap.png)

---
### Garbage Collection (GC) <a id="garbageCollection"></a>
Поколения сборщика мусора:   
G1 Young Generation - младшее поколение: G1 Eden Space, G1 Survivor Space.  
G1 Old Generation - старшее поколение: G1 Old Gen.
* GC Count - количество сборок мусора
* GC Time - время выполнения сборки мусора
* G1 Eden Space - пул памяти для новых объектов
* G1 Survivor Space - пул памяти для выживших объектов
* G1 Old Gen - пул памяти для долгоживущих объектов

![Garbage Collection (GC) - картинка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/GC.png)

---
### Threads <a id="threads"></a>
Состояние потоков.
* Threads - кол-во потоков по состояниям.
  * CURRENT - пользовательские потоки, которые используются для задач переднего плана и ввода-вывода в приложении. 
  JVM ждёт завершения их выполнения.
  * DAEMON - потоки с низким приоритетом, которые работают в фоновом режиме и выполняют задачи, например, сбор мусора,
  или предоставляют услуги пользовательским потокам.   
  Когда все пользовательские потоки завершают выполнение, JVM автоматически завершает демонические потоки, даже если они ещё выполняются.
  * DEADLOCKED - потоки, которые долго ждут друг друга и не могут сделать дальнейший прогресс.
* Current Threads State - кол-во пользовательских потоков.
  * NEW - создан, но ещё не запущен.
  * RUNNABLE - активный поток, либо готов к выполнению и ждёт процессорного времени.
  * BLOCKED - ждёт захвата блокировки монитора, которую держит другой поток.
  * WAITING - ждёт, пока другой поток выполнит определённое действие.  
  Например, если вызвать Object.wait() на объекте, то поток будет ждать, пока другой поток вызовет Object.notify() или
  Object.notifyAll() на этом объекте.
  * TIMED WAITING - ждёт определённое количество времени, пока другой поток выполнит определённое действие.  
  Например, если вызвать Thread.sleep() или Object.wait(timeout). В этом состоянии поток будет находиться до тех пор, 
  пока не истечёт указанный срок или другой поток не уведомит его.
  * TERMINATED - завершил выполнение или был прерван из-за исключения или ошибки.
  * UNKNOWN - состояние потока неизвестно.

![Threads - картинка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/Threads.png)

---
### Native Memory <a id="nativeMemory"></a>
Содержит несколько пулов памяти.
* Metaspace - пул памяти для хранения метаданных классов.
* Direct Buffer Pool - пул памяти, из которого можно выполнить прямое чтение. Используется для операций ввода-вывода.
* Mapped Buffer Pool - пул памяти для FileChannel-инстанций.
* CodeHeap Non-Nmethods - пул памяти, содержащий буферы компилятора и интерпретатор байт-кода.
* CodeHeap Non-Profiled Nmethods - пул памяти содержит полностью оптимизированные методы, которые живут долго.
* CodeHeap Profiled Nmethods - пул памяти содержит слегка оптимизированные методы, которые могут не понадобиться ещё раз.

![Native Memory - картинка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/Native_Memory.png)

---
## Настройка окружения <a id="settings"></a>

---
### Prometheus и Node-exporter <a id="prometheusNodeExporter"></a>
1. Установить и настроить [Prometheus](https://prometheus.io/docs/prometheus/latest/getting_started/)  
   Установить на Linux можно с помощью bash-скрипта -->
   [install-prometheus.sh](https://github.com/promokk/bash-scripts/blob/main/install-scripts/install-prometheus.sh)
   * Добавить новый job в файл конфигурации prometheus /etc/prometheus/prometheus.yml.  
     Вместо {host} необходимо указать свои сервера.

~~~shell
  # prometheus.yml
  scrape_configs:        
    - job_name: 'node_exporter'
      scrape_interval: 10s
      static_configs:
        - targets: [
          '{host}:9100',
          '{host}:9100'
          ]
 ~~~

2. Установить и настроить [Node-exporter](https://github.com/prometheus/node_exporter)  
   Установить на Linux можно с помощью bash-скрипта --> 
   [install-node-exporter.sh](https://github.com/promokk/bash-scripts/blob/main/install-scripts/install-node-exporter.sh)

---
### Jmx-exporter <a id="jmxExporter"></a>
Jmx-exporter запускается как java-agent при запуске Jmeter. Один java-agent собирает метрики с одного процесса Jmeter.
При запуске распределенного теста на master-сервере запускается два процесса Jmeter (jmeter и jmeter-server).
Поэтому в prometheus.yml для каждого сервера нужно указать минимум по два порта для jmx-exporter.
1. Создать файл targetJMX.json в директории /prometheus (Например: /etc/prometheus/targetJMX.json)  
   Вместо {host} и {port} необходимо указать сервера и порты выделенные под jmx-exporter.

~~~shell
# targetJMX.json
[
  {
    "labels": {
    "job": "jmx_exporter"
    },
    "targets": [
      "{host01}:{port01}",
      "{host01}:{port02}",
      "{host02}:{port01}",
      "{host02}:{port02}"
    ]
  }
]
~~~

2. Добавить новый job в конфигурационный файл prometheus /etc/prometheus/prometheus.yml.

~~~shell
# prometheus.yml
scrape_configs:
  - job_name: 'jmx_exporter'
    scrape_interval: 10s
    file_sd_configs:
      - files:
        - 'targetJMX.json'
~~~

3. Скачать [Jmx-exporter](https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_httpserver/)
4. Создать конфигурационный файл config.yaml для Jmx-exporter

~~~shell
# config.yaml
rules:
  - pattern: ".*"
~~~

5. Файл **jmx_prometheus_javaagent-*.jar** и **config.yaml** переместить 
   в директорию /jmeter/bin (Например: /opt/jmeter/bin)

---
### Jmeter <a id="jmeter"></a>
Чтобы запустить jmx-exporter вместе с Jmeter нужно отредактировать файл jmeter и jmeter-server.  
Файлы доступны в репозитории --> [jmeter-file/](https://github.com/promokk/jmeter-jmx-dashboard/tree/main/jmeter-file)
* /opt/jmeter/bin/jmeter
  * JMETER_PATH - путь до директории /jmeter/bin
  * jmx_prometheus_javaagent-*.jar - укажите свою версию jmx-exporter (Например: jmx_prometheus_javaagent-0.20.0.jar)

~~~shell
# jmeter
# Port jmx_prometheus_javaagent
JMX_EXPORTER_PORT=$1
# Jmeter path
JMETER_PATH="/opt/jmeter/bin"
shift

"$JAVA_HOME/bin/java" $ARGS $JVM_ARGS $JMETER_OPTS -javaagent:$JMETER_PATH/jmx_prometheus_javaagent-*.jar=$JMX_EXPORTER_PORT:$JMETER_PATH/config.yaml -jar "$PRGDIR/ApacheJMeter.jar" "$@"
~~~

* /opt/jmeter/bin/jmeter-server

~~~shell
# jmeter-server
# Port jmx_prometheus_javaagent
JMX_EXPORTER_PORT=$1
shift

${DIRNAME}/jmeter02 ${JMX_EXPORTER_PORT} ${RMI_HOST_DEF} -Dserver_port=${SERVER_PORT:-1099} -s -j jmeter-server.log "$@"
~~~

---
### Запуск Jmeter в Non-GUI mode <a id="runJmeter"></a>
Документация: [распределенноый запуск](https://jmeter.apache.org/usermanual/remote-test.html), 
[параметры командной строки Jmeter](https://jmeter.apache.org/usermanual/get-started.html#non_gui).  
При запуске необходимо указать **JMX_EXPORTER_PORT** - порт jxm-exporter, который ранее был указан в файле targetJMX.json

~~~shell
# Пример для запуска с одного сервера
# 1 - На выбранном сервере запускаем jmeter
nohup /opt/jmeter/bin/jmeter {JMX_EXPORTER_PORT01} -n -t scriptExample.jmx > /dev/null 2>&1&

# Пример для распределенного запуска
# 1 - На всех выбранных серверах запускаем jmeter-server
nohup /opt/jmeter/bin/jmeter-server {JMX_EXPORTER_PORT01} > /dev/null 2>&1&
# 2 - На master-сервере запускаем jmeter
nohup /opt/jmeter/bin/jmeter {JMX_EXPORTER_PORT02} -n -t scriptExample.jmx -X -R server01,server02 -Dmode=StrippedAsynch > /dev/null 2>&1&
~~~
