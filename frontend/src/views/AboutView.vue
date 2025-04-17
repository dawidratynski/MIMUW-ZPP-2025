<script setup>
import { Mail, Phone, Globe } from 'lucide-vue-next'
</script>

<template>
  <section class="container">
    <div>
      <h2 class="section-title">O projekcie</h2>
      <p class="paragraph">
        CleanTheWorld to aplikacja mobilna, która umożliwia użytkownikom zgłaszanie napotkanych odpadów
        poprzez zdjęcia. Wykorzystujemy sztuczną inteligencję do klasyfikacji odpadów na kategorie
        takie jak papier, szkło, plastik czy metal. Dane z lokalizacją trafiają do naszej bazy,
        skąd mogą być przekazywane odpowiednim służbom zajmującym się recyklingiem lub utrzymaniem
        czystości.
      </p>
    </div>

    <div>
      <h2 class="section-title">O fundacji</h2>
      <p class="paragraph">
        Jesteśmy organizacją non-profit wspierającą edukację, badania&nbsp;i rozwój nowych technologii – 
        w&nbsp;szczególności sztucznej inteligencji&nbsp;i informatyki kwantowej, ale również innych dziedzin 
        matematyki&nbsp;i informatyki. Fundacja została założona 20.11.2019 przez Pawła Gorę&nbsp;i działa na 
        terenie Polski.
      </p>
      <p class="paragraph">
        Organizujemy spotkania (np. Warsaw Quantum Computing Group), warsztaty, konkursy&nbsp;i hackathony. 
        Uczestniczymy w&nbsp;międzynarodowej inicjatywie P-TECH&nbsp;i wspieramy edukację m.in. uczniów I LO w&nbsp;Krakowie. 
        Współpracujemy także z&nbsp;QWorld, koordynując lokalną inicjatywę QPoland.
      </p>
    </div>


    <div class="contact-section">
      <h3 class="contact-title">Kontakt</h3>
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

