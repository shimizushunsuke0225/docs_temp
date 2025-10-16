{
  "family": "your-task-family",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["EC2"],
  "containerDefinitions": [
    {
      "name": "app",
      "image": "your-app-image:latest",
      "essential": true,
      "linuxParameters": {
        "capabilities": {
          "add": ["SYS_PTRACE"]
        }
      },
      "dockerSecurityOptions": ["seccomp=unconfined"],
      "memory": 4096,
      "cpu": 1024,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/your-log-group",
          "awslogs-region": "ap-northeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "MALLOC_ARENA_MAX", "value": "2" },
        { "name": "MALLOC_TRIM_THRESHOLD_", "value": "131072" },
        { "name": "MALLOC_MMAP_THRESHOLD_", "value": "131072" }
      ]
    }
  ]
}
