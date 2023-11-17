function initStationSearch()
{
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

    $("#tagdisplay1").click(function (e) 
    { 
        // If the clicked element has the class 'delete-button' 
        if (e.target.classList.contains('deletebtn')) { 
            
            // Remove the parent element (the tag) 
            e.target.parentNode.remove();

            let values = $('#tagdisplay1 li').map(function()
            {
                return $(this).contents().get(0).nodeValue; 
            }).get().join(','); 

            $("#txtags").val(values)
        } 
    }); 

    $('#tagsearch1').keyup(function()
    {
        var search = $(this).val().trim();
        if(search != "")
        {
            $.ajax(
            {
                url:"gettags",
                method:"POST",
                data:{filter:search},
                success:function(data)
                {
                    if (data)
                    {
                    $("#tagres1").html(data);

                    $("#tagres1 li").click(function(e) 
                    { 
                        let tagContent = e.target.innerText.trim(); 
                        if (tagContent !== "")
                        { 
                            let litag = document.createElement("li"); 
                            litag.innerText = tagContent; 
                            // Add delete button
                            litag.innerHTML += "<button class=\"deletebtn\">X</button>"; 
                            $("#tagdisplay1").append(litag); 
                            let values = $('#tagdisplay1 li').map(function()
                            {
                                return $(this).contents().get(0).nodeValue; 
                            }).get().join(','); 

                            $("#txtags").val(values);
                            $("#tagsearch1").focus();
                        }
                    });
                    }
                    else
                    {
                    $("#tagres1").html("No tag found.");
                    }

                    $("#tagres1").show();
                }
            });
        }
    });

    $("#tagsearch1").focus(function()
    {
        if($("#tagres1").html())
        {
            if(!$("#tagres1").is(":visible"))
            {
                $("#tagres1").show();
            }
        }
    });


    window.addEventListener("click", function(e)
    {   
        if (!$("#tagres1")[0].contains(e.target) && e.target.id != "tagsearch1")
        {
        if($("#tagres1").is(":visible"))
        {
            $("#tagres1").hide();
        }
        }
    });
}