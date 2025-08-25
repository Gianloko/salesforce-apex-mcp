public without sharing class ProductResource extends Resource {
    public static final String uri = '@server://services';
    public static final String resourceName = 'product-catalog';
    public static final String resourceTitle = 'Catalog of products';
    public static final String resourceDescription = 'List of all available products';
    public static final String resourceMimeType = 'application/json';
    public static Long resourceSize = 65536;

    public ProductResource() {
        super(uri, resourceName, resourceTitle, resourceDescription, resourceMimeType, resourceSize);
    }

    public override List<Resource.Content> read() {
        // The method MUST retrieve List<Content>
        List<Product2> products = [SELECT Id, Name, Description FROM Product2 LIMIT 10];

        List<Resource.Content> result = new List<Resource.Content>();
        for (Product2 product : products) {
            result.add(new Resource.Content(this.uri + '/' + product.Id, String.isNotBlank(product.Name) ? product.Name : 'Test', String.isNotBlank(product.Name) ? product.Name : 'Test', String.isNotBlank(product.Description) ? product.Description : 'Test'));
        }

        return result;
    }
}