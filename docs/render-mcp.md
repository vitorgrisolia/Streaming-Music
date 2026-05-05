# Render MCP setup

Use this configuration in Cursor (`~/.cursor/mcp.json`) and Claude Code.

## Cursor

```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer <RENDER_API_KEY>"
      }
    }
  }
}
```

## Claude Code

```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <RENDER_API_KEY>"
```

## Useful prompts

- `Set my Render workspace to <workspace-name>`
- `Show recent deploy failures for <service-name>`
- `Analyze the latest build log and return the most likely root cause`
- `Propose minimal fixes in build command, start command, and env vars`
