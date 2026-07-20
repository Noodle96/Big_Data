kafka-flink-streaming-lab/
│
├── infrastructure/
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── __main__.py
│   ├── config.py
│   ├── networking.py
│   ├── security.py
│   ├── ec2.py
│   └── outputs.py
│
├── scripts/
│   ├── kafka/
│   │   ├── install.sh
│   │   ├── broker.sh
│   │   └── topics.sh
│   │
│   └── flink/
│       ├── install.sh
│       ├── jobmanager.sh
│       └── taskmanager.sh
│
├── producer/
│   └── producer.py
│
├── consumer/
│   └── consumer.py
│
├── flink-job/
│   ├── pom.xml
│   └── src/
│
├── docs/
│   ├── images/
│   ├── diagrams/
│   ├── notes.md
│   └── laboratory.md
│
├── README.md
│
└── .gitignore
