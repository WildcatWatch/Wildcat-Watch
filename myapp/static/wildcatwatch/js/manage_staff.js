 document.addEventListener('DOMContentLoaded', function() {
            const editModal = document.getElementById('editModal');
            const closeBtn = editModal.querySelector('.close-btn');
            const editButtons = document.querySelectorAll('.btn-edit');
            
            editButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const dutyId = this.dataset.dutyId;
                    const staffId = this.dataset.staffId;
                    
                    document.getElementById('modalDutyId').value = dutyId;
                    document.getElementById('modalStaffId').value = staffId;
                    
                    document.getElementById('modalStaffName').value = this.dataset.staffName; 
                    document.getElementById('modalTitle').value = this.dataset.title;
                    document.getElementById('modalLocation').value = this.dataset.location;
                    document.getElementById('modalDescription').value = this.dataset.desc || '';
                    document.getElementById('modalTimeStart').value = this.dataset.start;
                    document.getElementById('modalTimeEnd').value = this.dataset.end;
                    
                    editModal.style.display = 'block';
                });
            });

            closeBtn.addEventListener('click', function() {
                editModal.style.display = 'none';
            });

            window.addEventListener('click', function(event) {
                if (event.target == editModal) {
                    editModal.style.display = 'none';
                }
            });
        });