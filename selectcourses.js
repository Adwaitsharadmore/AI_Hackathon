
function toggleCheckbox(courseCard) {
  const checkbox = courseCard.querySelector('.course-checkbox');
  checkbox.checked = !checkbox.checked;
  courseCard.classList.toggle('selected', checkbox.checked);
}

