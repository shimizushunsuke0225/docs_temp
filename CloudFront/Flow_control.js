function handler(event) {
    var request = event.request;
    var headers = request.headers;

    // Cookieヘッダーが存在するか確認
    if (headers.cookie) {
        var cookies = headers.cookie[0].value;
        // sessionidを探す
        var sessionMatch = cookies.match(/sessionid=([^;]+)/);
        if (sessionMatch && sessionMatch[1]) {
            // sessionidが存在する → 通す
            return request;
        }
    }

    // sessionidがない → sorryページへリダイレクト
    return {
        statusCode: 302,
        statusDescription: 'Found',
        headers: {
            'location': { value: '/sorry.html' }
        }
    };
}
