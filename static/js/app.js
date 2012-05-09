$('#last_plot').hide();

$('#current_plot').click(function (){
    $(this).slideUp();
    $('#last_plot').slideToggle();
});

$('#last_plot').click(function (){
    $(this).slideUp();
    $('#current_plot').slideToggle();
});

$('#plot_canvas img').dblclick(function (){
    window.open($(this).attr('src'));
});
