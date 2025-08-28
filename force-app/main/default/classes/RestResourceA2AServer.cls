@RestResource(UrlMapping='/a2a/*')
global without sharing class RestResourceA2AServer {

    @HttpPost
    global static void doPost() {
        try {
            String requestBody = RestContext.request.requestBody.toString();
            System.debug('### Request Body: ' + requestBody);

            RestResourceA2AServer.A2AMessage a2AClientMessage = (RestResourceA2AServer.A2AMessage) JSON.deserialize(requestBody, RestResourceA2AServer.A2AMessage.class);

            System.debug('### A2A Client Message: ' + JSON.serializePretty(a2AClientMessage));

            RestResourceA2AServer.A2AMessage a2AServerMessage = new RestResourceA2AServer.A2AMessage();
            a2AServerMessage.id = a2AClientMessage.id;
            a2AServerMessage.jsonrpc = '2.0';

            // --- Generate IDs ---
            String contextId = System.UUID.randomUUID().toString();
            String taskId = System.UUID.randomUUID().toString();
            String messageId = System.UUID.randomUUID().toString();

            // --- Create Task (this is what should be returned as result) ---
            RestResourceA2AServer.Task task = new RestResourceA2AServer.Task();
            task.id = taskId;
            task.contextId = contextId;
            task.kind = 'task';  // This must be 'task'
            task.status = new RestResourceA2AServer.TaskStatus();
            task.status.state = 'completed';
            task.status.timestamp = DateTime.now().formatGmt('yyyy-MM-dd\'T\'HH:mm:ss.SSS\'Z\'');
            task.history = new List<Message>();
            task.artifacts = new List<Artifact>();

            // --- Create Agent Message ---
            RestResourceA2AServer.Message agentMsg = new RestResourceA2AServer.Message();
            agentMsg.messageId = messageId;
            agentMsg.taskId = taskId;
            agentMsg.contextId = contextId;
            agentMsg.kind = 'message';
            agentMsg.role = 'agent';
            agentMsg.parts = new List<Parts>();

            // --- Create Text Part ---
            RestResourceA2AServer.Parts agentPart = new RestResourceA2AServer.Parts();
            agentPart.kind = 'text';  // Set kind on the Parts object

            String userMessage = (a2AClientMessage.params != null &&
                    a2AClientMessage.params.message != null &&
                    a2AClientMessage.params.message.parts != null &&
                    !a2AClientMessage.params.message.parts.isEmpty() &&
                    a2AClientMessage.params.message.parts[0].root != null &&
                    a2AClientMessage.params.message.parts[0].root.text != null)
                    ? a2AClientMessage.params.message.parts[0].root.text
                    : 'Hello from user';

            if (userMessage.toLowerCase().contains('product catalog')) {
                agentPart.text = 'Here is our product catalog:\n\n' +
                        '• GenWatt Diesel 1000kW - High-capacity industrial generator\n' +
                        '• GenWatt Diesel 200kW - Medium-capacity generator\n' +
                        '• GenWatt Diesel 10kW - Small-scale generator\n' +
                        '• Installation: Industrial - High - Professional installation service\n' +
                        '• SLA: Silver - Premium support package';
            } else {
                agentPart.text = 'Hello from A2A Server! You said: "' + userMessage + '"';
            }

            agentMsg.parts.add(agentPart);

            // --- Add message to task history ---
            task.history.add(agentMsg);

            // --- Set task as result (not the message directly) ---
            a2AServerMessage.result = task;

            String responseJson = JSON.serializePretty(a2AServerMessage, true);
            System.debug('### Response JSON: ' + responseJson);

            // --- Response ---
            RestContext.response.addHeader('Content-Type', 'application/json');
            RestContext.response.addHeader('Access-Control-Allow-Origin', '*');
            RestContext.response.addHeader('Access-Control-Allow-Methods', '*');
            RestContext.response.addHeader('Access-Control-Allow-Headers', '*');
            RestContext.response.statusCode = 200;
            RestContext.response.responseBody = Blob.valueOf(responseJson);

        } catch (Exception e) {
            System.debug('### Exception in doPost: ' + e.getMessage() + ', ' + e.getLineNumber());

            Map<String, Object> errorResponse = new Map<String, Object>{
                    'id' => null,
                    'jsonrpc' => '2.0',
                    'error' => new Map<String, Object>{
                            'code' => -32603,
                            'message' => 'Internal error: ' + e.getMessage()
                    }
            };

            RestContext.response.addHeader('Content-Type', 'application/json');
            RestContext.response.statusCode = 500;
            RestContext.response.responseBody = Blob.valueOf(JSON.serialize(errorResponse));
        }
    }

    @HttpGet
    global static void doGet() {
        A2APublicCard card = new A2APublicCard();
        card.protocolVersion = '0.3.0';
        card.version = '1.0.0';
        card.name = 'Salesforce A2A Server';
        card.description = 'A simple A2A Agent from Salesforce';
        card.preferredTransport = 'JSONRPC';
        card.capabilities = new Capabilities();
        card.capabilities.streaming = false;
        card.capabilities.pushNotifications = false;
        card.capabilities.stateTransitionHistory = true;
        card.supportsAuthenticatedExtendedCard = false;
        card.url = '<Insert your Rest Resource A2A endpoint>';
        card.defaultInputModes = new List<String>{'text'};
        card.defaultOutputModes = new List<String>{'text'};
        card.skills = new List<RestResourceA2AServer.Skills>();

        RestResourceA2AServer.Skills skill = new RestResourceA2AServer.Skills();
        skill.id = 'general_assistant';
        skill.name = 'General Assistant';
        skill.description = 'Provide product catalog and general assistance';
        skill.tags = new List<String>{'products','catalog','hello','assistance'};
        skill.examples = new List<String>{'product catalog','hello world','help me'};
        card.skills.add(skill);

        RestContext.response.addHeader('Content-Type', 'application/json');
        RestContext.response.addHeader('Access-Control-Allow-Origin', '*');
        RestContext.response.statusCode = 200;
        RestContext.response.responseBody = Blob.valueOf(JSON.serializePretty(card,true));
    }

    // === DTOs ===
    public class A2AMessage {
        public String id {get;set;}
        public String jsonrpc {get;set;}
        public String method {get;set;}
        public Params params {get;set;}
        public Task result {get;set;} // Changed back to Task
    }

    public class Params {
        public Message message {get;set;}
    }

    public class Task {
        public String id {get;set;}
        public String contextId {get;set;}
        public String kind {get;set;}
        public TaskStatus status {get;set;}
        public List<Message> history {get;set;}
        public List<Artifact> artifacts {get;set;}
    }

    public class Message {
        public String messageId {get;set;}
        public String taskId {get;set;}
        public String contextId {get;set;}
        public String kind {get;set;}
        public String role {get;set;}
        public List<Parts> parts {get;set;}
    }

    public class Parts {
        public String kind {get;set;}  // Added kind field here
        public String text {get;set;}  // Moved text here from TextPart
        public TextPart root {get;set;} // Keep for backward compatibility if needed
    }

    public class TextPart {
        public String kind {get;set;}
        public String text {get;set;}
    }

    public class Artifact {
        public String artifactId {get;set;}
        public String name {get;set;}
        public List<Parts> parts {get;set;}
    }

    public class A2APublicCard {
        public String protocolVersion {get;set;}
        public String name {get;set;}
        public String preferredTransport {get;set;}
        public String description {get;set;}
        public List<Skills> skills {get;set;}
        public List<String> defaultOutputModes {get;set;}
        public Boolean supportsAuthenticatedExtendedCard {get;set;}
        public List<String> defaultInputModes {get;set;}
        public String url {get;set;}
        public Capabilities capabilities {get;set;}
        public String version {get;set;}
    }

    public class Skills {
        public String id {get;set;}
        public String name {get;set;}
        public String description {get;set;}
        public List<String> tags {get;set;}
        public List<String> examples {get;set;}
    }

    public class Capabilities {
        public Boolean streaming {get;set;}
        public Boolean pushNotifications {get;set;}
        public Boolean stateTransitionHistory {get;set;}
    }

    public class TaskStatus {
        public String state {get;set;}
        public String timestamp {get;set;}
    }
}
