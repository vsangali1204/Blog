document.getElementById('sidebarToggle').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('collapsed');
    document.getElementById('content').classList.toggle('collapsed');
    
    // Check for small screen
    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').style.width = 
            document.getElementById('sidebar').classList.contains('collapsed') ? '100%' : '80px';
    }
});
