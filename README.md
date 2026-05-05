# Jmeter-jmx-dashboard
Дашборд Grafana для мониторинга JMX-метрик процесса Jmeter.  
Позволяет отслеживать утилизацию ресурсов Jmeter во время теста.  
Для работы дашборда используется Prometheus, [Jmx-exporter](https://github.com/prometheus/jmx_exporter)
и [Node-exporter](https://github.com/prometheus/node_exporter).

Дашборд доступен в [Grafana Labs](https://grafana.com/grafana/dashboards/22106-jmeter-jmx-dashboard/).

---
# Оглавление
* [Описание дашборда](#dashboardDescription)
  * [Parameters](#parameters)
  * [Summary](#summary)
  * [CPU / Memory](#cpuMemory)
  * [Heap / NonHeap](#heapNonHeap)
  * [Garbage Collection (GC)](#garbageCollection)
  * [Threads](#threads)
  * [Native Memory](#nativeMemory)
* [Настройка окружения](#settings)
  * [Prometheus и Node-exporter](#prometheusNodeExporter)
  * [Jmx-exporter](#jmxExporter)
  * [SD Server](#sdServer)
  * [Jmeter](#jmeter)
  * [Запуск Jmeter в Non-GUI mode](#runJmeter)

---
## Описание дашборда <a id="dashboardDescription"></a>
Чтобы писать производительные скрипты, нужно понимать, сколько ресурсов потребляют разные вариации скриптов Jmeter.  
Данный дашборд поволяет отслеживать утилизацию Jmeter во время теста.  
Node-exporter работает на сервере постоянно. Он необходим для панелей CPU.  
Jmx-exporter запускается как java-agent при запуске Jmeter, следовательно, завершает свою работу по окончанию теста.  
Процессы Jmeter создаются при запуске теста и завершают свою работу по окончанию теста. Кол-во генераторов нагрузки
всегда разное, поэтому необходимо добиться динамическое создание / удаление целей (targets) для системы мониторинга. 
Для хранения целей реализован легковесный HTTP SD Server (Service Discovery).

Архитектура:  
[JMeter Server] → запускает тест → POST action == 'register' на [SD Server] → цель создается  
[SD Server]     → хранит список целей в оперативной памяти  
[Prometheus]    → переодически отправляет запрос GET - получает цели с метками (lables)  
[JMeter Server] → завершает тест → POST action == 'unregister' на [SD Server] → цель удаляется

---
###  Parameters <a id="parameters"></a>
Параметры для выбора объекта анализа.
* data_source - источник данных
* script_name - наименование скрипта
* process_name - наименование процесса
* server - сервер

![Parameters - картинка](https://raw.githubusercontent.com/promokk/jmeter-jmx-dashboard/main/data/Parameters.png)

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
  > :warning: WARNING    
  > На изображении GC Count измеряется во времени - неверно. Это исправлено, измеряется в единицах.
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
### Prometheus / VictoriaMetrics и Node-exporter <a id="prometheusNodeExporter"></a>
1. Установить и настроить Prometheus / VictoriaMetrics  
   Установить на Linux можно с помощью bash-скрипта →
   [install-prometheus.sh](https://github.com/promokk/bash-scripts/blob/main/install-scripts/install-prometheus.sh) /
   [install-victoriametrics.sh](https://github.com/promokk/bash-scripts/blob/main/install-scripts/install-victoriametrics.sh)  
   Для VictoriaMetrics single-node нужно указать доп. флаг при запуске, чтобы переиспользовать конфигурационный файл:  
   ~~~shell
   -promscrape.config={path}/prometheus.yml
   ~~~
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
   Установить на Linux можно с помощью bash-скрипта → 
   [install-node-exporter.sh](https://github.com/promokk/bash-scripts/blob/main/install-scripts/install-node-exporter.sh)

---
### Jmx-exporter <a id="jmxExporter"></a>
Jmx-exporter запускается как java-agent при запуске Jmeter. Один java-agent собирает метрики с одного процесса Jmeter.
При запуске распределенного теста на master-сервере запускается два процесса Jmeter (jmeter и jmeter-server).

1. Добавить новый job в конфигурационный файл prometheus /etc/prometheus/prometheus.yml.

~~~shell
# prometheus.yml
scrape_configs:
  - job_name: 'jmx_exporter'
    scrape_interval: 10s
    http_sd_configs:
      - url: 'http://localhost:8089'
        refresh_interval: 10s
~~~

2. Скачать [Jmx-exporter](https://github.com/prometheus/jmx_exporter/releases)
3. Создать конфигурационный файл config.yaml для Jmx-exporter.

~~~shell
# config.yaml
rules:
  - pattern: ".*"
~~~

4. Файл **jmx_prometheus_javaagent-*.jar** и **config.yaml** переместить 
   в директорию /jmeter/bin (Например: /opt/jmeter/bin) на каждом генераторе нагрузки.

---
### SD Server <a id="sdServer"></a>
HTTP SD Server (Service Discovery) реализован с помощью python → [sd_server.py](https://github.com/promokk/jmeter-jmx-dashboard/blob/main/sd_server/sd_server.py)  
Приложение не хранит метрики. Оно выполняет только одну задачу - обнаружение целей. 
Цели сохраняются в оперативную память приложения.  

Взаимодействие с sd-server осуществляется через rest-запросы:
* GET / - получить список целей
* POST / - создать / удалить цель
~~~shell
# Request body
# create
{"action":"register","port":"{port}","script":"{script}","hostname":"{hostname}","process_name":"{process_name}"}
# delete
{"action":"unregister","port":"{port}"}

# action - тип операции
# port - порт, на котором запущен экспортер
# script - наименование скрипта
# hostname - хостнейм или ip-адрес сервера
# process_name - наименование процесса
~~~ 

SD Server необходимо запустить на сервере  prometheus / victoriaMetrics.  
Можно запустить как фоновый процесс или как службу:
1. Фоновый процесс

~~~shell
nohup python3 ./sd_server.py > /dev/null 2>&1 &
~~~

2. Служба (сервис)  
   Установить на Linux можно с помощью bash-скрипта → [install-sd-server.sh](https://github.com/promokk/jmeter-jmx-dashboard/blob/main/sd_server/install-sd-server.sh)
~~~shell
# /etc/systemd/system/sd-server.service
[Unit]
Description=Prometheus / VictoriaMetrics HTTP Service Discovery (SD) Server
After=network.target

[Service]
Type=simple
User=sd-server
Group=sd-server
WorkingDirectory=/opt/sd-server
ExecStart=/usr/bin/python3 /opt/sd-server/sd_server.py
Restart=always
RestartSec=5
# or for example - journal
StandardOutput=append:/var/log/sd-server/sd_server.log 
StandardError=append:/var/log/sd-server/sd_server.log

[Install]
WantedBy=multi-user.target
~~~

---
### Jmeter <a id="jmeter"></a>
Чтобы запустить jmx-exporter вместе с Jmeter нужно отредактировать файл jmeter и jmeter-server.  
При запуске / завершение процессов jmeter происходит запрос в sd-server для изменения списка целей.  
Файлы доступны в репозитории → [jmeter-file/](https://github.com/promokk/jmeter-jmx-dashboard/tree/main/jmeter-file)
* /opt/jmeter/bin/jmeter
  * JMX_EXPORTER_PORT - порт jmx-exporter
  * SD_ENDPOINT - полный адрес sd-server (например: http://{host}:{port})
  * JMETER_PATH - путь до директории /jmeter/bin
  * jmx_prometheus_javaagent-*.jar - версия jmx-exporter (Например: jmx_prometheus_javaagent-1.5.0.jar)

~~~shell
# Port jmx_prometheus_javaagent
JMX_EXPORTER_PORT=$1
# Host:Port sd_server
SD_ENDPOINT=$2
# Jmeter path
JMETER_PATH="/opt/jmeter/bin"
shift 2

# === HTTP SD SERVER REGISTRATION ===
# Defining the host name
CLIENT_HOSTNAME=$(hostname -f 2>/dev/null || hostname)
# Process name (jmeter / jmeter-server
PROCESS_NAME="${PROCESS_NAME:-jmeter}"

# Extract script name (works with -t script.jmx and -t=script.jmx)
SCRIPT_NAME="unknown"
next_is_name=""
for arg in "$@"; do
  case "$arg" in
    -t) next_is_name="1"; continue ;;
    -t=*) SCRIPT_NAME=$(basename "${arg#-t=}" .jmx); break ;;
  esac
  if [ "$next_is_name" = "1" ]; then
    SCRIPT_NAME=$(basename "$arg" .jmx)
    break
  fi
done

# Target registration
curl -sf -m 3 -X POST -H "Content-Type: application/json" \
  -d "{\"action\":\"register\",\"port\":\"${JMX_EXPORTER_PORT}\",\"script\":\"${SCRIPT_NAME}\",\"hostname\":\"${CLIENT_HOSTNAME}\",\"process_name\":\"${PROCESS_NAME}\"}" \
  "$SD_ENDPOINT" >/dev/null 2>&1 || echo "!!! Failed to register target with SD server !!!"

# Automatic removal of the target at any completion
trap 'curl -sf -m 3 -X POST -H "Content-Type: application/json" \
  -d "{\"action\":\"unregister\",\"port\":\"${JMX_EXPORTER_PORT}\"}" \
  "$SD_ENDPOINT" >/dev/null 2>&1' EXIT INT TERM
# === END HTTP SD SERVER ===

"$JAVA_HOME/bin/java" $ARGS $JVM_ARGS $JMETER_OPTS -javaagent:$JMETER_PATH/jmx_prometheus_javaagent-1.5.0.jar=$JMX_EXPORTER_PORT:$JMETER_PATH/config.yaml -jar "$PRGDIR/ApacheJMeter.jar" "$@"
~~~

* /opt/jmeter/bin/jmeter-server

~~~shell
# Port jmx_prometheus_javaagent
JMX_EXPORTER_PORT=$1
# Host:Port sd_server
SD_ENDPOINT=$2
shift 2

# Process name (jmeter / jmeter-server)
export PROCESS_NAME="${PROCESS_NAME:-jmeter-server}"

${DIRNAME}/jmeter-jmx ${JMX_EXPORTER_PORT} ${SD_ENDPOINT} ${RMI_HOST_DEF} -Dserver_port=${SERVER_PORT:-1099} -s -j jmeter-server.log "$@"
~~~

---
### Запуск Jmeter в Non-GUI mode <a id="runJmeter"></a>
Документация: [распределенноый запуск](https://jmeter.apache.org/usermanual/remote-test.html), 
[параметры командной строки Jmeter](https://jmeter.apache.org/usermanual/get-started.html#non_gui).  
При запуске необходимо указать параметры:
* MX_EXPORTER_PORT - порт jmx-exporter
* SD_ENDPOINT - полный адрес sd-server (например: http://{host}:{port})
* для jmeter-server как и для jmeter нужно указать наименование скрипта через флаг -t.  
  Это нужно для корректной записи метки script для jmeter-server при сохранении цели.

~~~shell
# Пример для запуска с одного сервера
# 1 - На выбранном сервере запускаем jmeter
nohup /opt/jmeter/bin/jmeter-jmx {JMX_EXPORTER_PORT01} "{SD_ENDPOINT}" -n -t scriptExample.jmx > /dev/null 2>&1&

# Пример для распределенного запуска
# 1 - На всех выбранных серверах запускаем jmeter-server
nohup /opt/jmeter/bin/jmeter-server-jmx {JMX_EXPORTER_PORT01} "{SD_ENDPOINT}" -t scriptExample.jmx > /dev/null 2>&1&
# 2 - На master-сервере запускаем jmeter
nohup /opt/jmeter/bin/jmeter-jmx {JMX_EXPORTER_PORT02} "{SD_ENDPOINT}" -n -t scriptExample.jmx -R server01,server02 -Dmode=StrippedAsynch > /dev/null 2>&1&
~~~
