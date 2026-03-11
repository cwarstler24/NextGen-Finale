<template>
  <div class="app-shell">
    <nav class="top-nav">
      <span class="brand">
        <svg class="brand-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="36" height="36" aria-hidden="true">
          <!-- Burger bun (top) -->
          <path d="M12 26 Q12 16 32 16 Q52 16 52 26 Z" fill="#e8a045"/>
          <!-- Burger sesame seeds -->
          <ellipse cx="24" cy="20" rx="2" ry="1.2" fill="#c47a20" transform="rotate(-20 24 20)"/>
          <ellipse cx="34" cy="18.5" rx="2" ry="1.2" fill="#c47a20" transform="rotate(10 34 18.5)"/>
          <ellipse cx="43" cy="21" rx="2" ry="1.2" fill="#c47a20" transform="rotate(-10 43 21)"/>
          <!-- Lettuce -->
          <path d="M12 28 Q18 25 24 28 Q30 31 36 28 Q42 25 52 28 L52 30 Q42 27 36 30 Q30 33 24 30 Q18 27 12 30 Z" fill="#5cb85c"/>
          <!-- Burger patty -->
          <rect x="12" y="30" width="40" height="6" rx="2" fill="#7b3f00"/>
          <!-- Cheese -->
          <path d="M10 36 L54 36 L52 40 L12 40 Z" fill="#f5c518"/>
          <!-- Burger bun (bottom) -->
          <path d="M12 40 L52 40 L52 44 Q52 48 32 48 Q12 48 12 44 Z" fill="#e8a045"/>
          <!-- Flying saucer dome (inside burger) -->
          <ellipse cx="32" cy="33" rx="8" ry="4.5" fill="#a0d8ef" opacity="0.9"/>
          <!-- Flying saucer rim (inside burger) -->
          <ellipse cx="32" cy="35" rx="13" ry="3" fill="#7ec8e3"/>
          <!-- Saucer rim highlight (inside burger) -->
          <ellipse cx="32" cy="34" rx="9" ry="1.5" fill="#b8e0f0" opacity="0.6"/>
          <!-- Saucer window (inside burger) -->
          <ellipse cx="32" cy="32" rx="3" ry="2" fill="#d0f0ff" opacity="0.8"/>
          <!-- Saucer window glint (inside burger) -->
          <ellipse cx="30.5" cy="31.5" rx="0.8" ry="0.5" fill="white" opacity="0.7"/>
        </svg>
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
