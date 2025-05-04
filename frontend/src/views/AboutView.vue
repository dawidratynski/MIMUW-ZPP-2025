<script setup>
import { Mail, Phone, Globe } from 'lucide-vue-next'
</script>

<template>
  <section class="container">
    <div>
      <h2 class="section-title">{{ $t('about_project') }}</h2>
      <p class="paragraph">
        {{ $t('project_paragraph') }}
      </p>
    </div>

    <div>
      <h2 class="section-title">{{ $t('about_foundation') }}</h2>
      <p class="paragraph">
        {{ $t('foundation_paragraph1') }}
      </p>
      <p class="paragraph">
        {{ $t('foundation_paragraph2') }}
      </p>
    </div>


    <div class="contact-section">
      <h3 class="contact-title">{{ $t('contact') }}</h3>
      <ul class="contact-list">
        <li class="contact-item">
          <Globe class="icon blue" />
          <span>
            <a href="https://www.qaif.org" target="_blank">https://www.qaif.org</a>,
            <a href="http://www.mimuw.edu.pl/~pawelg" target="_blank">http://www.mimuw.edu.pl/~pawelg</a>
          </span>
        </li>
        <li class="contact-item">
          <Mail class="icon" />
          <span>
            <a href="mailto:warsaw.quantum@gmail.com">warsaw.quantum@gmail.com</a>,
            <a href="mailto:pawel.gora@qaif.org">pawel.gora@qaif.org</a>
          </span>
        </li>
        <li class="contact-item">
          <Phone class="icon" />
          <span>+48 507 982 292</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.container {
  padding: 3rem 1.5rem 4rem;
  max-width: 768px;
  margin: 0 auto;
  text-align: justify;
}

.section-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-align: center;
}

.paragraph {
  margin-bottom: 1rem;
  color: #4a4a4a;
}

.contact-section {
  padding-top: 2rem;
  border-top: 1px solid #ccc;
}

.contact-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
}

.contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  color: #4a4a4a;
}

.contact-item a {
  color: #2563eb;
  text-decoration: none;
  margin-right: 0.5rem;
}

.contact-item a:hover {
  text-decoration: underline;
}

.icon {
  width: 24px;
  height: 24px;
  color: #333;
}

.icon.blue {
  color: #2563eb;
}
</style>

