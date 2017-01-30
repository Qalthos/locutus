$vg(function() {
    // Toggle plot display when you click a label.
    $vg('g.activate-serie').click(function() {
        var plot_id = this.id.split('-')[2];
        $vg('g.serie-'+plot_id).toggle();
    });
});
