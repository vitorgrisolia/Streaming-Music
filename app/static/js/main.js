(() => {
  const path = window.location.pathname;

  const isActive = (linkPath) => {
    if (linkPath === '/') {
      return path === '/';
    }
    return path === linkPath || path.startsWith(`${linkPath}/`);
  };

  document.querySelectorAll('.nav-link').forEach((link) => {
    try {
      const linkPath = new URL(link.href).pathname;
      if (isActive(linkPath)) {
        link.classList.add('is-active');
      }
    } catch (error) {
      // ignora links invalidos
    }
  });

  const animatedElements = Array.from(document.querySelectorAll('[data-animate]'));
  animatedElements.forEach((element, index) => {
    if (!element.style.getPropertyValue('--delay')) {
      element.style.setProperty('--delay', `${Math.min(index * 45, 360)}ms`);
    }
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in-view');
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.08,
        rootMargin: '0px 0px -35px 0px',
      }
    );

    animatedElements.forEach((element) => observer.observe(element));
  } else {
    animatedElements.forEach((element) => element.classList.add('in-view'));
  }

  const flashMessages = document.querySelectorAll('.messages .msg');
  if (flashMessages.length > 0) {
    window.setTimeout(() => {
      flashMessages.forEach((message) => {
        message.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
        message.style.opacity = '0';
        message.style.transform = 'translateY(-6px)';
      });
    }, 5500);
  }

  const audioElement = document.querySelector('audio');
  if (audioElement) {
    audioElement.addEventListener('play', () => {
      document.body.classList.add('is-playing');
    });

    audioElement.addEventListener('pause', () => {
      document.body.classList.remove('is-playing');
    });

    audioElement.addEventListener('ended', () => {
      document.body.classList.remove('is-playing');
    });
  }
})();
