overlayBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    titleInput.value = img.alt.replace('Cover of ', '');
    form.submit();
});