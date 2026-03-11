<template>
  <div class="app-shell">
    <nav class="top-nav">
    <span class="brand">
        <img src="/images/Logo.jpg" style="width: 3em" alt="Logo" class="brand-icon" />
        <RouterLink to="/" class="brand-name"> The Frying Saucer </RouterLink>
      </span>
      <div class="nav-links">
        <RouterLink to="/burger">Burger</RouterLink>
        <RouterLink to="/fries">Fries</RouterLink>
      </div>
    </nav>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-icon {
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
