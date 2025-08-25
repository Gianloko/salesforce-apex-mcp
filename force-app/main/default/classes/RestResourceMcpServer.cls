@RestResource(UrlMapping='/mcp/*')
global without sharing class RestResourceMcpServer {

    @HttpPost
    global static void post() {

        /**for(String header: RestContext.request.headers.keySet()){
            System.debug('### header: ' + header + ' --> ' + RestContext.request.headers.get(header));
        }**/

        //System.debug('### request body: ' + RestContext.request.requestBody.toString());

        Server server = new Server('1.0.0', 'salesforce-mcp-server', 'Salesforce MCP Server', 'MCP Server to expose CRM data');
        server.registerTool(new LeadTool());
        server.registerResource(new ProductResource());
        server.registerPrompt(new CodeReviewPrompt());
        server.run();
    }
}