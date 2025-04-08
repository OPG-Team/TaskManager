document.addEventListener("DOMContentLoaded", () => {
    const applyFiltersButton = document.getElementById("applyFilters");
    const clearFiltersButton = document.getElementById("clearFilters");
    const filterStatus = document.getElementById("filterStatus");
    const filterTimeAfter = document.getElementById("filterTimeAfter");

    const setDefaultDate = () => {
        const today = new Date();
        const lastMonth = new Date(today.setMonth(today.getMonth() - 1));
        filterTimeAfter.valueAsDate = lastMonth;
    };
    
    setDefaultDate();

    applyFiltersButton.addEventListener("click", () => {
        const selectedStatus = filterStatus.value;
        const selectedDate = filterTimeAfter.value;
        filterTasks(selectedStatus, selectedDate);
    });

    clearFiltersButton.addEventListener("click", () => {
        filterStatus.value = "";
        setDefaultDate();
        filterTasks("", "");
    });

    function filterTasks(status, date) {
        const taskItems = document.querySelectorAll(".task-item");

        taskItems.forEach(taskItem => {
            const taskStatus = taskItem.querySelector(".task-status span").textContent;
            
            const dateText = taskItem.querySelector(".task-view p:nth-child(4)").textContent;
            const taskDateStr = dateText.replace("Created: ", "");
            const taskDate = new Date(taskDateStr);

            taskDate.setHours(0, 0, 0, 0);
            
            const filterDate = date ? new Date(date) : null;
            if (filterDate) {
                filterDate.setHours(0, 0, 0, 0);
            }

            const matchesStatus = status === "" || taskStatus === status;
            const matchesDate = !filterDate || taskDate >= filterDate;

            taskItem.style.display = matchesStatus && matchesDate ? "block" : "none";
        });
    }
});