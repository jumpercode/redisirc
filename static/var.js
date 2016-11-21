
function ajaxEnviar(url, data, fn)
{
	$.ajax(
	{
    	contentType: 'application/json; charset=utf-8',
    	dataType: 'json',
		type: 'POST',
     	url: url,
     	data: JSON.stringify(data),
     	success: function(json)
      	{
      		fn(json);
      	}
	});
}

