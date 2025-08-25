global class Ping {

    public String id        {get;set;}
    public Result result    {get;set;}
    public String jsonrpc   {get;set;}

    public Ping(String id, String jsonrpc){
        this.id = id;
        this.jsonrpc = jsonrpc;
        this.result = new Result();
    }

    public class Result {}
}