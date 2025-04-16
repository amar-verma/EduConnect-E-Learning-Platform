
                    // Weekly Active Students Chart
                    const ctx1e = document.getElementById('studentsChart').getContext('2d');
                    new Chart(ctx1e, {
                      type: 'line',
                      data: {
                        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        datasets: [{
                          label: 'Active Students',
                          data: [120, 150, 180, 220, 200, 250, 300],
                          borderColor: '#4caf50',
                          fill: true,
                          backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        }]
                      },
                      options: { responsive: true }
                    });
                
                    // Course Enrollments by Category Chart
                    const ctx2e = document.getElementById('coursesChart').getContext('2d');
                    new Chart(ctx2e, {
                      type: 'doughnut',
                      data: {
                        labels: ['Programming', 'Design', 'Data Science', 'Marketing', 'Others'],
                        datasets: [{
                          data: [40, 25, 20, 10, 5],
                          backgroundColor: ['#4caf50', '#fbc02d', '#03a9f4', '#e91e63', '#9e9e9e'],
                        }]
                      },
                      options: { responsive: true }
                    });
            