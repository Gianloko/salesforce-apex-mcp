public with sharing class CodeReviewPrompt extends Prompt {
    public CodeReviewPrompt() {
        super('code_review', 'Code Review', 'Asks the LLM to analyze code quality and suggest improvements');

        this.addArgument(new Prompt.Argument('code', 'The code to review', true));
    }

    public override List<Prompt.Message> get(Map<String, Object> input) {
        String code = (String) input.get('code');

        List<Prompt.Message> messages = new List<Prompt.Message>();

        messages.add(new Prompt.Message('user', 'Review the following code and suggest improvements: ' + code));

        return messages;
    }
}