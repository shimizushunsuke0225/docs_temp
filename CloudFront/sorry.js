function handler(event) {
    var request = event.request;
    var uri = request.uri;
  
    if (
      uri.startsWith("/aaa") ||
      uri.startsWith("/bbb") ||
      uri.startsWith("/ccc/xyz")
    ) {
      return {
        statusCode: 302,
        statusDescription: "Found",
        headers: {
          "location": { value: "/sorry.html" }
        }
      };
    }
  
    return request;
  }
  