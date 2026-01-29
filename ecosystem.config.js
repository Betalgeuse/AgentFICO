module.exports = {
  apps: [
    {
      name: "agentfico-api",
      script: "python3",
      args: "-m uvicorn api.src.main:app --host 0.0.0.0 --port 8000",
      interpreter: "none",
      cwd: "/Users/zayden/Documents/web3_folder/AgentFICO",
      env: {
        PYTHONPATH: "/Users/zayden/Documents/web3_folder/AgentFICO",
        AGENTFICO_CONFIG_PATH: "/Users/zayden/Documents/web3_folder/AgentFICO-Config",
      },
      env_production: {
        PYTHONPATH: "/Users/zayden/Documents/web3_folder/AgentFICO",
        AGENTFICO_CONFIG_PATH: "/etc/agentfico/config",
        NODE_ENV: "production",
      },
      watch: false,
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 1000,
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      error_file: "./logs/api-error.log",
      out_file: "./logs/api-out.log",
      merge_logs: true,
    },
  ],
};
