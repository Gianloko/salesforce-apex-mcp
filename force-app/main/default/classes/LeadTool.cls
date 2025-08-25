public without sharing class LeadTool extends Tool {
    public LeadTool() {
        super('create-leads', 'Create New Leads', 'Create a new Lead record into Salesforce database');

        Tool.Property leadLastnameProp = new Tool.Property('leadLastName', 'string', 'Lead Last Name', true);
        this.addProperty(leadLastnameProp);
    }

    public override String call(Map<String, Object> input) {
        String leadLastName = (String) input.get('leadLastName');
        Lead leadToCreate = new Lead(
            LastName = leadLastName
        );
        insert(leadToCreate);
        return JSON.serializePretty(leadToCreate);
    }
}