const skillLevelRange = document.getElementById('skillLevelRange');
const skillLevelValue = document.getElementById('skillLevelValue');

if (skillLevelRange && skillLevelValue) {
    skillLevelRange.addEventListener('input', function () {
        skillLevelValue.textContent = this.value;
    });
}
