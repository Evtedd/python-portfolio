import { useState, useEffect, useRef, useCallback, memo } from 'react';
import { HERO_IMAGE, PRODUCT_IMAGES, PRODUCT_PRICES, PROMO_CODES, getPrice, getStartPrice } from './catalog.js';

// Photos config imported from catalog.js
const PHOTOS = { hero: { wide: HERO_IMAGE }, ...PRODUCT_IMAGES };

function getImg(k, m) {
  const e = PHOTOS[k];
  if (!e) return "";
  if (typeof e === "string") return e;
  if (m === "wide" || m === "hero") return e.wide || e.product || e.card || "";
  if (m === "card") return e.card || e.product || "";
  if (m === "product") return e.product || e.card || "";
  return e.product || e.card || "";
}

// DESIGN TOKENS (static, outside render)
const C = {
  accent: "#c9a96e", accentH: "#dbb878", accentD: "#a07d4a",
  bg: "#0a0a0a", card: "#0f0f0f", card2: "#131313", card3: "#0d0d0d",
  text: "#f0ece4", sec: "#8a8478", muted: "#5a564e",
  border: "#1a1a1a", sans: "'Inter','Helvetica Neue',sans-serif",
  green: "#4a8b5c", red: "#8b4a4a"
};

const labelStyle = { fontFamily: C.sans, fontSize: "10px", letterSpacing: "4.5px", textTransform: "uppercase", color: C.accent, marginBottom: "16px", display: "block" };
const sectionPad = { padding: "140px 24px", maxWidth: "1200px", margin: "0 auto" };

function btnPrimary(x = {}) {
  return { background: C.accent, color: C.bg, border: "none", padding: "15px 40px", fontFamily: C.sans, fontSize: "10.5px", fontWeight: 600, letterSpacing: "3px", textTransform: "uppercase", cursor: "pointer", transition: "background .3s", ...x };
}
function btnOutline(x = {}) {
  return { ...btnPrimary(x), background: "transparent", color: C.text, border: `1px solid ${C.muted}`, transition: "border-color .3s, color .3s" };
}
const inputStyle = { width: "100%", padding: "14px 16px", background: C.card, border: `1px solid ${C.border}`, color: C.text, fontFamily: C.sans, fontSize: "13px", transition: "border-color .3s", boxSizing: "border-box" };

// NMH branded social icons with one visual language
const NmhIconInstagram = ({size=20}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="2" width="20" height="20" rx="6" stroke="#c9a96e" strokeWidth="1.5"/>
    <circle cx="12" cy="12" r="5" stroke="#c9a96e" strokeWidth="1.5"/>
    <circle cx="18" cy="6" r="1.2" fill="#c9a96e"/>
  </svg>
);
const NmhIconTelegram = ({size=20}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3.5 11.3L20.5 4.5C20.5 4.5 21.5 4.1 21.3 5L19 16.5C19 16.5 18.8 17.5 17.9 17.1L12 12.8L9.5 15.2C9.5 15.2 9.3 15.4 9 15.3L9.5 11.8L18.5 5.8L7.5 12.3L3.5 11.3Z" fill="#c9a96e"/>
  </svg>
);
const NmhIconWhatsApp = ({size=20}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2C6.48 2 2 6.28 2 11.5C2 13.52 2.7 15.38 3.88 16.88L2.5 21.5L7.3 20.15C8.72 20.94 10.32 21.38 12 21.38C17.52 21.38 22 17.1 22 11.88C22 6.66 17.52 2 12 2Z" stroke="#c9a96e" strokeWidth="1.5"/>
    <path d="M8.5 10C8.5 10 8.5 8.5 10 8.5C11.5 8.5 11.5 10 11.5 10L11.5 11C11.5 11 11.5 11.5 12 12C12.5 12.5 13 12.5 13 12.5L14 12.5C14 12.5 15.5 12.5 15.5 14C15.5 15.5 14 15.5 14 15.5" stroke="#c9a96e" strokeWidth="1.3" strokeLinecap="round"/>
  </svg>
);
const NmhIconEmail = ({size=20}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2" y="5" width="20" height="14" rx="2" stroke="#c9a96e" strokeWidth="1.5"/>
    <path d="M2 7L12 13L22 7" stroke="#c9a96e" strokeWidth="1.5"/>
  </svg>
);

// TRANSLATIONS (condensed)
const T = {
en: {
  nav:{home:"Home",house:"The House",signature:"Signature",initiation:"Initiation",privateEd:"Private Editions",ritual:"Ritual Objects",journal:"Journal",support:"Support"},
  hero:{title:"Where Silence Becomes Scent",sub:"A private fragrance house for those who speak in presence, not volume.",cta1:"Enter the House",cta2:"Signature Collection"},
  sigBlock:{label:"Signature Collection",title:"The Foundation of the House",sub:"Five compositions. Five codes. The permanent vocabulary of Noir Maison Haute."},
  houseStructure:{label:"The House Structure",title:"Four Levels of the House",sub:"A system with layers, access, and hierarchy.",levels:[
    {name:"Signature Collection",desc:"The permanent foundation."},
    {name:"Initiation",desc:"Luxury entry with sealed archive samples."},
    {name:"Private Editions",desc:"Time coded. Never repeated."},
    {name:"Ritual Objects",desc:"Designer objects of the ritual."}
  ]},
  privateBlock:{label:"Private Editions",title:"Released from the Archive",sub:"Limited allocations. Each carries a code that will not return."},
  ritualBlock:{label:"Ritual Objects",title:"Objects of the Ritual",sub:"Designer objects extending scent into space and silence."},
  houseSection:{label:"The House",title:"Built on Silence and Obsession",p1:"We are a fragrance house born from the belief that scent is the last truly private luxury.",p2:"Every composition is designed for men who don't need to announce their presence.",p3:"Our bottles are hand finished. Our formulas are private."},
  journal:{label:"Journal",title:"Notes from the House",articles:[
    {tag:"Scent Story",title:"The Architecture of Oud",excerpt:"Why the rarest wood became the foundation of modern masculine fragrance."},
    {tag:"Ritual",title:"How to Wear Fragrance in Winter",excerpt:"Cold air changes everything. A guide to the close encounter."},
    {tag:"Campaign",title:"After Hours",excerpt:"Behind the lens, shot at 3AM in an unnamed hotel."}
  ]},
  faq:{label:"FAQ",title:"Frequently Asked Questions",items:[
    {q:"How do I choose a fragrance?",a:"Start with the Initiation Case."},
    {q:"What payment methods are available?",a:"BTC, ETH, LTC, TRX, BNB, SOL, USDT (5 networks), USDC (5 networks). Network selection at checkout."},
    {q:"How long does delivery take?",a:"Ships within 48 hours. International 5 to 12 business days."},
    {q:"Can I return?",a:"Unopened items within 14 days. Private Editions are final sale."},
  ]},
  product:{addToCart:"Add to Cart",buyNow:"Buy Now",topNotes:"Top Notes",heartNotes:"Heart Notes",baseNotes:"Base Notes",mood:"Mood",volume:"Volume",story:"The Story",howItWears:"How It Wears",intensity:"Intensity",season:"Season",longevity:"Longevity",editionIdentity:"Edition Identity",editionType:"Type",releaseCode:"Code",unitsProduced:"Units",archiveStatus:"Archive Status",collectorNote:"Collector Note",dispatch:"Ships within 48 hours",shippingNote:"Free shipping above",returns:"14 day returns on unopened items",alsoLove:"You May Also Love"},
  footer:{tagline:"Silence is the ultimate luxury.",rights:"All rights reserved.",terms:"Terms",privacy:"Privacy",refund:"Refund",shipping:"Shipping",payment:"Payment"},
  cart:{title:"Your Selection",empty:"Your cart is empty",total:"Total",subtotal:"Subtotal",shipping:"Shipping",free:"Free",checkout:"Proceed to Checkout",remove:"Remove",cont:"Continue Shopping"},
  checkout:{title:"Checkout",email:"Email",shipping:"Shipping Address",name:"Full Name",address:"Address",city:"City",country:"Country",zip:"Postal Code",agree:"I agree to the Terms and Privacy Policy",proceed:"Continue to Payment",selectCurrency:"Select Payment Method",selectNetwork:"Select Network",paymentDetails:"Payment Details",sendExactly:"Send exactly",toAddress:"to the address below",copyAddress:"Copy Address",copied:"Copied!",wrongNetwork:"⚠ Send only on the selected network.",waitingPayment:"Waiting for payment...",orderConfirmed:"Order Confirmed",orderSuccess:"Your order has been placed. Confirmation email sent.",orderNumber:"Order Number",backHome:"Return Home",processing:"Processing...",trackOrder:"Track Order",timeRemaining:"Time remaining"},
  support:{title:"Support",sub:"We are here to help.",contactForm:"Send a Message",formName:"Name",formEmail:"Email",formSubject:"Subject",formMessage:"Message",formTelegram:"Telegram (optional)",formSend:"Send",formSent:"Message sent.",formError:"Error. Please try again."},
  orderStatus:{title:"Order Status",orderId:"Order ID",status:"Status",statuses:{created:"Created",awaiting_payment:"Awaiting Payment",awaiting_confirmation:"Verifying Payment",confirmed:"Confirmed",paid:"Paid",shipped:"Shipped",completed:"Completed",cancelled:"Cancelled"}}
},
ru: {
  nav:{home:"Главная",house:"О Доме",signature:"Signature",initiation:"Initiation",privateEd:"Private Editions",ritual:"Ritual Objects",journal:"Журнал",support:"Поддержка"},
  hero:{title:"Где тишина становится ароматом",sub:"Закрытый па��фюмерный дом для тех, кто говорит присутствием.",cta1:"Войти в Дом",cta2:"Signature Collection"},
  sigBlock:{label:"Signature Collection",title:"Основа Дома",sub:"Пять композиций. Пять кодов."},
  houseStructure:{label:"Архитектура Дома",title:"Четыре уровня",sub:"Система с уровнями и иерархией.",levels:[{name:"Signature Collection",desc:"Постоянная основа."},{name:"Initiation",desc:"Премиальный вход."},{name:"Private Editions",desc:"Не повторяются."},{name:"Ritual Objects",desc:"Объекты ритуала."}]},
  privateBlock:{label:"Private Editions",title:"Из архива",sub:"Ограниченные тиражи."},
  ritualBlock:{label:"Ritual Objects",title:"Объекты ритуала",sub:"Расширяют мир аромата."},
  houseSection:{label:"Дом",title:"Построен на тишине",p1:"Парфюмерный дом, рождённый из убеждения, что аромат является последней приватной роскошью.",p2:"Композиции для мужчин, которым не нужно объявлять о присутствии.",p3:"Флаконы обработаны вручную. Формулы закрыты."},
  journal:{label:"Журнал",title:"Заметки из Дома",articles:[{tag:"История",title:"Архитектура уда",excerpt:"Редчайшее дерево как основа."},{tag:"Ритуал",title:"Аромат зимой",excerpt:"Холодный воздух меняет всё."},{tag:"Кампания",title:"After Hours",excerpt:"Съёмка в 3 часа ночи."}]},
  faq:{label:"FAQ",title:"Частые вопросы",items:[{q:"Как выбрать?",a:"Начните с Initiation Case."},{q:"Способы оплаты?",a:"BTC, ETH, LTC, TRX, BNB, SOL, USDT, USDC. Выбор сети при оплате."},{q:"Доставка?",a:"Отправка за 48ч. 5 до 12 рабочих дней."},{q:"Возврат?",a:"Невскрытые в течение 14 дней."}]},
  product:{addToCart:"В корзину",buyNow:"Купить",topNotes:"Верхние ноты",heartNotes:"Ноты сердца",baseNotes:"Базовые ноты",mood:"Настроение",volume:"Объём",story:"История",howItWears:"Как носится",intensity:"Интенсивность",season:"Сезон",longevity:"Стойкость",editionIdentity:"Идентичность",editionType:"Тип",releaseCode:"Код",unitsProduced:"Тираж",archiveStatus:"Архив",collectorNote:"Заметка",dispatch:"Отправка за 48 часов",shippingNote:"Бесплатная доставка от",returns:"Возврат 14 дней",alsoLove:"Также понравится"},
  footer:{tagline:"Тишина как высшая роскошь.",rights:"Все права защищены.",terms:"Условия",privacy:"Конфиденциальность",refund:"Возврат",shipping:"Доставка",payment:"Оплата"},
  cart:{title:"Ваш выбор",empty:"Корзина пуста",total:"Итого",subtotal:"Подитог",shipping:"Доставка",free:"Бесплатно",checkout:"К оплате",remove:"Удалить",cont:"Продолжить"},
  checkout:{title:"Оформление",email:"Email",shipping:"Адрес доставки",name:"Имя",address:"Адрес",city:"Город",country:"Страна",zip:"Индекс",agree:"Согласен с условиями",proceed:"К оплате",selectCurrency:"Способ оплаты",selectNetwork:"Выберите сеть",paymentDetails:"Детали оплаты",sendExactly:"Отправьте",toAddress:"на адрес",copyAddress:"Копировать",copied:"Скопировано!",wrongNetwork:"⚠ Только в выбранной сети.",waitingPayment:"Ожидание...",orderConfirmed:"Подтверждён",orderSuccess:"Заказ оформлен.",orderNumber:"Номер",backHome:"На главную",processing:"Обработка...",trackOrder:"Отследить",timeRemaining:"Осталось"},
  support:{title:"Поддержка",sub:"Мы здесь чтобы помочь.",contactForm:"Написать",formName:"Имя",formEmail:"Email",formSubject:"Тема",formMessage:"Сообщение",formTelegram:"Telegram",formSend:"Отправить",formSent:"Отправлено.",formError:"Ошибка."},
  orderStatus:{title:"Статус заказа",orderId:"Номер",status:"Статус",statuses:{created:"Создан",awaiting_payment:"Ожидание оплаты",awaiting_confirmation:"Проверка оплаты",confirmed:"Подтверждён",paid:"Оплачен",shipped:"Отправлен",completed:"Завершён",cancelled:"Отменён"}}
},
es: {
  nav:{home:"Inicio",house:"La Casa",signature:"Signature",initiation:"Initiation",privateEd:"Private Editions",ritual:"Ritual Objects",journal:"Diario",support:"Soporte"},
  hero:{title:"Donde el silencio se convierte en aroma",sub:"Una casa de fragancias privada para quienes hablan con presencia.",cta1:"Entrar a la Casa",cta2:"Signature Collection"},
  sigBlock:{label:"Signature Collection",title:"La Base de la Casa",sub:"Cinco composiciones. Cinco códigos."},
  houseStructure:{label:"Estructura",title:"Cuatro niveles",sub:"Un sistema con capas y jerarquía.",levels:[{name:"Signature Collection",desc:"Base permanente."},{name:"Initiation",desc:"Entrada de lujo."},{name:"Private Editions",desc:"Sin repetición."},{name:"Ritual Objects",desc:"Objetos del ritual."}]},
  privateBlock:{label:"Private Editions",title:"Del archivo",sub:"Asignaciones limitadas."},
  ritualBlock:{label:"Ritual Objects",title:"Objetos del ritual",sub:"Extienden el mundo del aroma."},
  houseSection:{label:"La Casa",title:"Silencio y obsesión",p1:"Una casa nacida de la creencia de que el aroma es el último lujo privado.",p2:"Composiciones para hombres que no necesitan anunciar su presencia.",p3:"Frascos terminados a mano. Fórmulas privadas."},
  journal:{label:"Diario",title:"Notas",articles:[{tag:"Historia",title:"Arquitectura del Oud",excerpt:"La madera más rara."},{tag:"Ritual",title:"Fragancia en invierno",excerpt:"El aire frío lo cambia todo."},{tag:"Campaña",title:"After Hours",excerpt:"A las 3AM."}]},
  faq:{label:"FAQ",title:"Preguntas frecuentes",items:[{q:"¿Cómo elijo?",a:"Comienza con el Initiation Case."},{q:"¿Pago?",a:"BTC, ETH, LTC, TRX, BNB, SOL, USDT, USDC."},{q:"¿Entrega?",a:"Envío en 48h. 5 a 12 días."},{q:"¿Devoluciones?",a:"14 días sin abrir."}]},
  product:{addToCart:"Añadir",buyNow:"Comprar",topNotes:"Notas de salida",heartNotes:"Corazón",baseNotes:"Fondo",mood:"Ambiente",volume:"Volumen",story:"Historia",howItWears:"Cómo se lleva",intensity:"Intensidad",season:"Temporada",longevity:"Longevidad",editionIdentity:"Edición",editionType:"Tipo",releaseCode:"Código",unitsProduced:"Unidades",archiveStatus:"Archivo",collectorNote:"Nota",dispatch:"Envío en 48h",shippingNote:"Envío gratis desde",returns:"14 días devolución",alsoLove:"También te gustará"},
  footer:{tagline:"El silencio es el lujo supremo.",rights:"Todos los derechos reservados.",terms:"Términos",privacy:"Privacidad",refund:"Devoluciones",shipping:"Envío",payment:"Pago"},
  cart:{title:"Tu selección",empty:"Vacío",total:"Total",subtotal:"Subtotal",shipping:"Envío",free:"Gratis",checkout:"Al pago",remove:"Eliminar",cont:"Seguir comprando"},
  checkout:{title:"Pago",email:"Email",shipping:"Dirección",name:"Nombre",address:"Dirección",city:"Ciudad",country:"País",zip:"Código postal",agree:"Acepto términos",proceed:"Al pago",selectCurrency:"Método",selectNetwork:"Red",paymentDetails:"Detalles",sendExactly:"Envía",toAddress:"a la dirección",copyAddress:"Copiar",copied:"¡Copiado!",wrongNetwork:"⚠ Solo en la red seleccionada.",waitingPayment:"Esperando...",orderConfirmed:"Confirmado",orderSuccess:"Pedido realizado.",orderNumber:"Número",backHome:"Inicio",processing:"Procesando...",trackOrder:"Rastrear",timeRemaining:"Tiempo"},
  support:{title:"Soporte",sub:"Estamos aquí.",contactForm:"Mensaje",formName:"Nombre",formEmail:"Email",formSubject:"Asunto",formMessage:"Mensaje",formTelegram:"Telegram",formSend:"Enviar",formSent:"Enviado.",formError:"Error."},
  orderStatus:{title:"Estado",orderId:"Número",status:"Estado",statuses:{created:"Creado",awaiting_payment:"Esperando pago",awaiting_confirmation:"Verificando pago",confirmed:"Confirmado",paid:"Pagado",shipped:"Enviado",completed:"Completado",cancelled:"Cancelado"}}
}};

// PRODUCT DATA (static, outside render)
const PRODUCTS = {
  signature: [
    {id:"nc",name:"Noir Code",sizes:["50 ml","100 ml"],cat:"signature",color:"#1a1510",top:"Bergamot · Pink Pepper · Saffron",heart:"Oud · Iris · Black Violet",base:"Amber · Musk · Ebony Wood",wear:{i:"8/10",s:"Autumn · Winter",l:"10+ hours"},photo:"noirCode",desc:{en:"Dark woods and cold glass",ru:"Тёмное дерево и холодное стекло",es:"Maderas oscuras"},mood:{en:"Midnight office.",ru:"Полуночный кабинет.",es:"Oficina de medianoche."},story:{en:"A scent that enters the room before you do.",ru:"Аромат, входящий раньше вас.",es:"Un aroma que entra antes."}},
    {id:"cr",name:"Cold Reserve",sizes:["50 ml","100 ml"],cat:"signature",color:"#12161a",top:"Cardamom · Grapefruit · Mint",heart:"Vetiver · Tobacco · Suede",base:"Sandalwood · Benzoin · Leather",wear:{i:"7/10",s:"All seasons",l:"8 to 10 hours"},photo:"coldReserve",desc:{en:"Smoke, leather, amber",ru:"Дым, кожа, амбра",es:"Humo, cuero, ámbar"},mood:{en:"Private dinner.",ru:"Закрытый ужин.",es:"Cena privada."},story:{en:"Restraint made tangible.",ru:"Сдержанность, ставшая осязаемой.",es:"Contención tangible."}},
    {id:"at",name:"After Trade",sizes:["50 ml","100 ml"],cat:"signature",color:"#161412",top:"Juniper · Lemon · White Pepper",heart:"Cedar · White Tea · Gin Accord",base:"Musk · Ambergris · Cashmere Wood",wear:{i:"6/10",s:"Spring · Summer",l:"7 to 9 hours"},photo:"afterTrade",desc:{en:"Clean luxury after midnight",ru:"Чистая роскошь",es:"Lujo limpio"},mood:{en:"Hotel suite.",ru:"Номер в отеле.",es:"Suite."},story:{en:"The cleanest scent and the most dangerous.",ru:"Самый чистый и опасный.",es:"El más limpio y peligroso."}},
    {id:"bl",name:"Black Ledger",sizes:["50 ml","100 ml"],cat:"signature",color:"#0f0e10",top:"Ink Accord · Black Pepper · Elemi",heart:"Saffron · Leather · Oud",base:"Labdanum · Castoreum · Ebony",wear:{i:"9/10",s:"Autumn · Winter",l:"12+ hours"},photo:"blackLedger",desc:{en:"Ink, leather, saffron",ru:"Чернила, кожа, шафран",es:"Tinta, cuero, azafrán"},mood:{en:"The archive room.",ru:"Комната архива.",es:"La sala de archivos."},story:{en:"Authority, quiet, absolute.",ru:"Власть, тихая, абсолютная.",es:"Autoridad, callada, absoluta."}},
    {id:"vs",name:"Velvet Static",sizes:["50 ml","100 ml"],cat:"signature",color:"#141318",top:"Ozone · Bergamot · Pink Pepper",heart:"Cashmere · Violet Leaf · Silver Birch",base:"White Musk · Suede · Ambroxan",wear:{i:"5/10",s:"Spring · Summer",l:"6 to 8 hours"},photo:"velvetStatic",desc:{en:"Cold air, electricity",ru:"Холодный воздух, электричество",es:"Aire frío, electricidad"},mood:{en:"Floor 47.",ru:"47 этаж.",es:"Piso 47."},story:{en:"Charged silence between decisions.",ru:"Заряженная тишина между решениями.",es:"Silencio cargado."}}
  ],
  initiation: [
    {id:"ic",name:"Initiation Case",sizes:["5 x 10 ml"],cat:"initiation",color:"#111",photo:"initiationCase",desc:{en:"Luxury entry into the House",ru:"Премиальный вход",es:"Entrada de lujo"},mood:{en:"The ritual begins.",ru:"Ритуал начинается.",es:"El ritual comienza."},story:{en:"Five miniatures, ritual guide, sealed archive sample, authentication card.",ru:"Пять миниатюр, гид, архивный сэмпл, карта подлинности.",es:"Cinco miniaturas, guía, muestra sellada, tarjeta."},included:{en:["5 x 10 ml Signature miniatures","Sealed Archive Sample","Authentication card","Ritual guide","Collector sleeve"],ru:["5 × 10 мл миниатюр","Архивный сэмпл","Карта подлинности","Гид","Футляр"],es:["5 x 10 ml miniaturas","Muestra sellada","Tarjeta","Guía","Funda"]}},
  ],
  privateEditions: [
    {id:"nc43",name:"Noir Code",code:"00:43",type:{en:"Hour Edition",ru:"Hour Edition",es:"Hour Edition"},sizes:["100 ml"],cat:"private",color:"#1a1510",photo:"noirCode0043",units:120,archiveStatus:{en:"From Private Archive",ru:"Из закрытого архива",es:"Del archivo privado"},collectorNote:{en:"Will not return in the same balance.",ru:"Не повторится.",es:"No volverá."},desc:{en:"Time coded: 00:43",ru:"Код времени: 00:43",es:"Codificación: 00:43"},mood:{en:"The hour the formula locked.",ru:"Час фиксации.",es:"La hora del cierre."}},
    {id:"fm",name:"Founder's Mark",code:"FM001",type:{en:"Founder's Mark",ru:"Founder's Mark",es:"Founder's Mark"},sizes:["100 ml"],cat:"private",color:"#0e0c08",photo:"foundersMarkEdition",units:50,archiveStatus:{en:"Hand marked by the Founder",ru:"Маркировано Основателем",es:"Marcado por el Fundador"},collectorNote:{en:"Will not be reissued.",ru:"Не будет переиздано.",es:"No se reeditará."},desc:{en:"Hand marked by the Founder",ru:"Маркировано вручную",es:"Marcado a mano"},mood:{en:"The most private release.",ru:"Самый закрытый выпуск.",es:"El más privado."}}
  ],
  ritualObjects: [
    {id:"nva",name:"Night Vessel Atomizer",sizes:["Item"],cat:"ritual",color:"#0e0e0e",photo:"nightVessel",desc:{en:"Metal and leather atomizer",ru:"Металлический атомайзер",es:"Atomizador de metal"},mood:{en:"The ritual continues.",ru:"Ритуал продолжается.",es:"El ritual continúa."}},
    {id:"sv",name:"Scent Vault",sizes:["Item"],cat:"ritual",color:"#111",photo:"scentVault",desc:{en:"Desktop scent object",ru:"Настольный объект",es:"Objeto de aroma"},mood:{en:"Atmosphere.",ru:"Атмосфера.",es:"Atmósfera."}},
    {id:"cm",name:"Cold Monolith",sizes:["Item"],cat:"ritual",color:"#0a0a0a",photo:"coldMonolith",desc:{en:"Stone aromatic sculpture",ru:"Каменная скульптура",es:"Escultura de piedra"},mood:{en:"Silence made material.",ru:"Тишина как материал.",es:"Silencio material."}},
    {id:"cc",name:"Collector Case",sizes:["Item"],cat:"ritual",color:"#0d0b08",photo:"collectorCase",desc:{en:"Display and storage",ru:"Кейс для хранения",es:"Estuche"},mood:{en:"Architecture.",ru:"Архитектура.",es:"Arquitectura."}}
  ]
};
const ALL_PRODUCTS = [...PRODUCTS.signature, ...PRODUCTS.initiation, ...PRODUCTS.privateEditions, ...PRODUCTS.ritualObjects];

// REVEAL cinematic entrance using GPU friendly motion
function Reveal({ children, delay = 0 }) {
  const ref = useRef(null);
  const [v, setV] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { setV(true); obs.disconnect(); }
    }, { threshold: 0.06, rootMargin: "0px 0px -60px 0px" });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);
  return (
    <div ref={ref} style={{
      opacity: v ? 1 : 0,
      transform: v ? "translateY(0)" : "translateY(28px)",
      transition: `opacity .85s cubic-bezier(.16,1,.3,1) ${delay}s, transform .85s cubic-bezier(.16,1,.3,1) ${delay}s`,
      willChange: v ? "auto" : "opacity, transform"
    }}>{children}</div>
  );
}

// IMAGE lazy loaded with CSS driven hover zoom
const NMHImage = memo(function NMHImage({ photoKey, name, mode = "card", height, style: xs = {} }) {
  const src = getImg(photoKey, mode);
  const dh = { hero: "56vw", card: "300px", product: "580px" };
  const h = height || dh[mode] || "300px";
  const isHero = mode === "hero" || mode === "wide";
  const isProduct = mode === "product";
  const cls = isProduct ? "nmh-prod-img" : mode === "card" ? "nmh-card-img" : "";

  if (src) return (
    <div className={cls} style={{ position: "relative", overflow: "hidden", width: "100%", height: h, ...xs }}>
      {/* Refined gradient overlay, warm and subtle */}
      <div style={{ position: "absolute", inset: 0, background: isProduct
        ? "linear-gradient(180deg, transparent 80%, rgba(0,0,0,0.2) 100%)"
        : "linear-gradient(180deg, rgba(0,0,0,0.03) 0%, transparent 30%, transparent 65%, rgba(0,0,0,0.35) 100%)",
        pointerEvents: "none", zIndex: 1 }} />
      <img
        src={src} alt={name}
        loading={isHero ? "eager" : "lazy"}
        decoding={isHero ? "sync" : "async"}
        style={{ display: "block", width: "100%", height: "100%", objectFit: "cover", objectPosition: "center" }}
      />
    </div>
  );

  const prod = ALL_PRODUCTS.find(p => p.photo === photoKey);
  const sz = isProduct ? 220 : mode === "card" ? 150 : 80;
  return (
    <div className={cls} style={{ width: "100%", height: h, display: "flex", justifyContent: "center", alignItems: "center", background: C.card, ...xs }}>
      <BottleSVG color={prod?.color || "#111"} size={sz} />
    </div>
  );
});

// SVG BOTTLE without drop shadow filter, clean static render
const BottleSVG = memo(function BottleSVG({ color = "#1a1510", size = 200 }) {
  const id = "b" + Math.random().toString(36).substr(2, 5);
  return (
    <svg viewBox="0 0 200 400" width={size} height={size * 1.5}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2=".6" y2="1">
          <stop offset="0%" stopColor={color} /><stop offset="100%" stopColor="#050505" />
        </linearGradient>
      </defs>
      <rect x="82" y="18" width="36" height="20" rx="3" fill={C.accent} opacity=".5" />
      <rect x="88" y="38" width="24" height="44" rx="3" fill={C.accent} opacity=".35" />
      <path d="M60,90 Q60,80 88,78 L112,78 Q140,80 140,90 L140,360 Q140,368 132,368 L68,368 Q60,368 60,360 Z" fill={`url(#${id})`} />
      <line x1="72" y1="210" x2="128" y2="210" stroke={C.accent} strokeWidth=".4" opacity=".25" />
      <text x="100" y="234" textAnchor="middle" fill={C.accent} fontSize="9" fontFamily="serif" letterSpacing="5" opacity=".4">NMH</text>
    </svg>
  );
});

// PRODUCT CARD with CSS driven hover, zoom, lift, and warm glow
const ProdCard = memo(function ProdCard({ prod, delay = 0, showCode = false, lang, onClick }) {
  return (
    <Reveal delay={delay}>
      <div className="nmh-card" onClick={() => onClick(prod)}
        style={{ background: showCode ? C.card3 : C.card, border: `1px solid ${C.border}`, cursor: "pointer", overflow: "hidden", position: "relative" }}>
        {showCode && <div style={{ position: "absolute", top: "12px", right: "12px", zIndex: 5, fontFamily: C.sans, fontSize: "9px", letterSpacing: "2px", color: C.muted, background: "rgba(10,10,10,.8)", backdropFilter: "blur(4px)", padding: "4px 10px", border: `1px solid ${C.border}` }}>{prod.code || "Limited"}</div>}
        <NMHImage photoKey={prod.photo} name={prod.name} mode="card" />
        <div style={{ padding: "24px 24px 28px" }}>
          <h3 style={{ fontSize: "21px", fontWeight: 300, letterSpacing: "1.5px", marginBottom: "5px" }}>{prod.name}</h3>
          {prod.code && <span style={{ fontFamily: C.sans, fontSize: "11px", color: C.accent, letterSpacing: "2px", display: "block", marginBottom: "5px" }}>{prod.code}</span>}
          <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, marginBottom: "16px", lineHeight: 1.5 }}>{prod.desc[lang]}</p>
          <span style={{ fontFamily: C.sans, fontSize: "16px", letterSpacing: "0.5px" }}>{Object.keys(PRODUCT_PRICES[prod.id]?.prices||{}).length > 1 ? `${lang==='ru'?'от':'from'} ` : ''}${getStartPrice(prod.id)}</span>
        </div>
      </div>
    </Reveal>
  );
});

// MAIN APP
export default function App() {
  const [lang, setLang] = useState(() => localStorage.getItem('nmh_lang') || 'en');
  const [page, setPage] = useState("home");
  const [cart, setCart] = useState(() => { try { return JSON.parse(localStorage.getItem('nmh_cart')) || []; } catch { return []; } });
  const [menu, setMenu] = useState(false);
  const [selProd, setSelProd] = useState(null);
  const [openFaq, setOpenFaq] = useState(null);
  const [toast, setToast] = useState(null);
  const [storeConfig, setStoreConfig] = useState(null);

  // User auth
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('nmh_token') || null);
  const [user, setUser] = useState(null);

  useEffect(() => { localStorage.setItem('nmh_cart', JSON.stringify(cart)); }, [cart]);
  useEffect(() => { localStorage.setItem('nmh_lang', lang); }, [lang]);
  useEffect(() => { if (authToken) localStorage.setItem('nmh_token', authToken); else localStorage.removeItem('nmh_token'); }, [authToken]);
  useEffect(() => { fetch('/api/config').then(r => r.json()).then(setStoreConfig).catch(() => {}); }, []);
  // Load user profile if token exists
  useEffect(() => {
    if (!authToken) { setUser(null); return; }
    fetch('/api/auth/me', { headers: { 'x-auth-token': authToken } })
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(setUser)
      .catch(() => { setAuthToken(null); setUser(null); });
  }, [authToken]);

  const authHeaders = authToken ? { 'x-auth-token': authToken, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
  const logout = () => { setAuthToken(null); setUser(null); go('home'); };

  const t = T[lang];

  // History API for browser back/forward
  const go = useCallback((p) => {
    setPage(p); setMenu(false);
    window.history.pushState({ page: p }, '', '/' + (p === 'home' ? '' : p));
    window.scrollTo({ top: 0 });
    // Analytics
    fetch('/api/analytics/visit', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page: p, lang, ua: navigator.userAgent }) }).catch(() => {});
  }, [lang]);

  const goProd = useCallback((p) => {
    setSelProd(p); setPage("product");
    window.history.pushState({ page: 'product', prodId: p.id }, '', '/product/' + p.id);
    window.scrollTo({ top: 0 });
    fetch('/api/analytics/visit', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page: 'product', product: p.name, lang, ua: navigator.userAgent }) }).catch(() => {});
  }, [lang]);

  // Handle browser back/forward
  useEffect(() => {
    const onPop = (e) => {
      const state = e.state;
      if (state && state.page) {
        setPage(state.page);
        if (state.prodId) {
          const prod = ALL_PRODUCTS.find(p => p.id === state.prodId);
          if (prod) setSelProd(prod);
        }
      } else { setPage('home'); }
      setMenu(false);
    };
    window.addEventListener('popstate', onPop);
    // Set initial state
    window.history.replaceState({ page: 'home' }, '', '/');
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  // Fragrance Finder state
  const [showFinder, setShowFinder] = useState(false);
  const [finderActive, setFinderActive] = useState(false);
  const productViewCount = useRef(0);

  // Show finder after viewing several products without adding to cart
  useEffect(() => {
    if (page === 'product') productViewCount.current++;
    if (productViewCount.current >= 3 && cart.length === 0 && !finderActive) {
      const timer = setTimeout(() => setShowFinder(true), 8000);
      return () => clearTimeout(timer);
    }
  }, [page, cart.length, finderActive]);
  const addCart = useCallback((p, sz) => {
    const itemPrice = getPrice(p.id, sz);
    setCart(c => [...c, { ...p, selectedSize: sz, price: itemPrice, cid: Date.now(), qty: 1 }]);
    setToast(lang === 'ru' ? 'Добавлено' : lang === 'es' ? 'Añadido' : 'Added');
    setTimeout(() => setToast(null), 1800);
  }, [lang]);
  const rmCart = useCallback((cid) => setCart(c => c.filter(i => i.cid !== cid)), []);
  const updateQty = useCallback((cid, q) => setCart(c => c.map(i => i.cid === cid ? { ...i, qty: Math.max(1, q) } : i)), []);

  const shipping = storeConfig?.shipping || { price: 25, freeAbove: 300 };
  const subtotal = cart.reduce((s, i) => s + i.price * i.qty, 0);
  const shippingCost = subtotal >= shipping.freeAbove ? 0 : shipping.price;
  const total = subtotal + shippingCost;

  // HEADER
  const Header = () => (
    <header style={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 1000, background: "rgba(10,10,10,.92)", backdropFilter: "blur(16px)", borderBottom: `1px solid ${C.border}` }}>
      <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "0 28px", height: "64px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ cursor: "pointer" }} onClick={() => go("home")}><span style={{ fontSize: "20px", fontWeight: 300, letterSpacing: "8px", textTransform: "uppercase" }}>NMH</span></div>
        <nav className="nmh-dnav" style={{ display: "flex", gap: "24px", alignItems: "center" }}>
          {[["signature", "signature"], ["initiation", "initiation"], ["privateEd", "private"], ["ritual", "ritual"], ["house", "about"], ["support", "support"]].map(([k, pg]) => (
            <span key={k} onClick={() => go(pg)} style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: page === pg ? C.accent : C.sec, cursor: "pointer", transition: "color .2s" }}
              onMouseEnter={e => { if (page !== pg) e.target.style.color = C.text; }} onMouseLeave={e => { if (page !== pg) e.target.style.color = C.sec; }}>{t.nav[k]}</span>
          ))}
          <span onClick={() => go("account")} style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: page === 'account' ? C.accent : C.sec, cursor: "pointer", transition: "color .2s" }}
            onMouseEnter={e => { if (page !== 'account') e.target.style.color = C.text; }} onMouseLeave={e => { if (page !== 'account') e.target.style.color = C.sec; }}>{user ? (user.name || '◆') : (lang === 'ru' ? 'Вход' : lang === 'es' ? 'Cuenta' : 'Account')}</span>
        </nav>
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div style={{ display: "flex", gap: "2px" }}>
            {["en", "ru", "es"].map(l => <span key={l} onClick={() => setLang(l)} style={{ fontFamily: C.sans, fontSize: "10px", textTransform: "uppercase", color: lang === l ? C.accent : C.muted, cursor: "pointer", padding: "4px 6px" }}>{l}</span>)}
          </div>
          <span onClick={() => go("cart")} style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.sec, cursor: "pointer", position: "relative" }}>
            Cart{cart.length > 0 && <span style={{ position: "absolute", top: "-5px", right: "-13px", background: C.accent, color: C.bg, borderRadius: "50%", width: "15px", height: "15px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "8px", fontWeight: 700 }}>{cart.reduce((s, i) => s + i.qty, 0)}</span>}
          </span>
          <span className="nmh-mbtn" onClick={() => setMenu(!menu)} style={{ cursor: "pointer", fontFamily: C.sans, fontSize: "11px", color: C.sec, display: "none" }}>{menu ? "✕" : "☰"}</span>
        </div>
      </div>
      {menu && <div style={{ position: "fixed", top: "64px", left: 0, right: 0, bottom: 0, background: "rgba(10,10,10,.97)", padding: "40px 28px", display: "flex", flexDirection: "column", gap: "22px", zIndex: 999, overflowY: "auto" }}>
        {[["signature", "signature"], ["initiation", "initiation"], ["privateEd", "private"], ["ritual", "ritual"], ["house", "about"], ["support", "support"], ["journal", "journal"]].map(([k, pg]) => <span key={k} onClick={() => go(pg)} style={{ fontSize: "22px", fontWeight: 300, cursor: "pointer" }}>{t.nav[k]}</span>)}
        <div style={{ display: "flex", gap: "10px", marginTop: "12px" }}>{[["en", "English"], ["ru", "Русский"], ["es", "Español"]].map(([l, lb]) => <span key={l} onClick={() => { setLang(l); setMenu(false); }} style={{ fontFamily: C.sans, fontSize: "11px", color: lang === l ? C.accent : C.muted, cursor: "pointer", padding: "6px 12px", border: `1px solid ${lang === l ? C.accent : C.border}` }}>{lb}</span>)}</div>
      </div>}
    </header>
  );

  // HOME cinematic hero with refined atmosphere
  const HomePage = () => (
    <>
      <section style={{ height: "100vh", display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center", textAlign: "center", position: "relative", overflow: "hidden" }}>
        {getImg("hero", "wide") ? (
          <div style={{ position: "absolute", inset: 0 }}>
            {/* Hero image with slow cinematic zoom, 20s and barely noticeable */}
            <img src={getImg("hero", "wide")} alt="" loading="eager" style={{
              width: "100%", height: "100%", objectFit: "cover",
              animation: "heroBreath 20s ease-in-out infinite alternate",
              transformOrigin: "center 40%"
            }} />
            {/* Refined overlay, clean with no dirty patches */}
            <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(10,10,10,.15) 0%, rgba(10,10,10,0) 35%, rgba(10,10,10,.45) 70%, rgba(10,10,10,.93) 100%)" }} />
            {/* Warm ambient glow from bottom */}
            <div style={{ position: "absolute", bottom: 0, left: "50%", transform: "translateX(-50%)", width: "80%", height: "40%", background: "radial-gradient(ellipse at center bottom, rgba(201,169,110,.04) 0%, transparent 70%)", pointerEvents: "none" }} />
          </div>
        ) : (
          <>
            <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 25%, #18150f 0%, #0a0a0a 55%)" }} />
            <div style={{ position: "absolute", bottom: 0, left: "50%", transform: "translateX(-50%)", width: "60%", height: "50%", background: "radial-gradient(ellipse at center bottom, rgba(201,169,110,.03) 0%, transparent 70%)", pointerEvents: "none" }} />
          </>
        )}
        <div style={{ position: "relative", zIndex: 1, maxWidth: "780px", padding: "0 24px", paddingBottom: "clamp(80px, 13vh, 160px)" }}>
          <Reveal delay={0.1}><h1 style={{ fontSize: "clamp(40px, 8vw, 80px)", fontWeight: 300, lineHeight: 1.05, letterSpacing: "0.5px", marginBottom: "26px" }}>{t.hero.title}</h1></Reveal>
          <Reveal delay={0.35}><p style={{ fontFamily: C.sans, fontSize: "14px", color: "rgba(240,236,228,.7)", lineHeight: 1.9, maxWidth: "460px", margin: "0 auto 52px" }}>{t.hero.sub}</p></Reveal>
          <Reveal delay={0.55}><div style={{ display: "flex", gap: "14px", justifyContent: "center", flexWrap: "wrap" }}>
            <button className="nmh-btn-p" style={btnPrimary()} onClick={() => go("signature")}>{t.hero.cta1}</button>
            <button className="nmh-btn-o" style={btnOutline()} onClick={() => go("about")}>{t.hero.cta2}</button>
          </div></Reveal>
        </div>
        {/* Scroll indicator with subtle pulse */}
        <div style={{ position: "absolute", bottom: "32px", left: "50%", transform: "translateX(-50%)", zIndex: 1 }}>
          <div style={{ width: "1px", height: "40px", background: `linear-gradient(to bottom, transparent, rgba(201,169,110,.35))`, opacity: 0.6 }} />
        </div>
      </section>

      {/* HOUSE STRUCTURE */}
      <section style={sectionPad}><Reveal><div style={{ textAlign: "center", marginBottom: "64px" }}><span style={labelStyle}>{t.houseStructure.label}</span><h2 style={{ fontSize: "clamp(26px, 4vw, 44px)", fontWeight: 300, marginBottom: "14px" }}>{t.houseStructure.title}</h2><p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, maxWidth: "560px", margin: "0 auto" }}>{t.houseStructure.sub}</p></div></Reveal>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "16px" }}>{t.houseStructure.levels.map((lv, i) => <Reveal key={i} delay={i * .06}><div onClick={() => go(["signature", "initiation", "private", "ritual"][i])} style={{ background: C.card, border: `1px solid ${C.border}`, padding: "36px 24px", cursor: "pointer", transition: "border-color .3s", height: "100%" }} onMouseEnter={e => e.currentTarget.style.borderColor = C.accentD} onMouseLeave={e => e.currentTarget.style.borderColor = C.border}><span style={{ fontFamily: C.sans, fontSize: "9px", letterSpacing: "3px", color: C.accent, display: "block", marginBottom: "14px" }}>0{i + 1}</span><h3 style={{ fontSize: "18px", fontWeight: 300, marginBottom: "10px" }}>{lv.name}</h3><p style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec, lineHeight: 1.7 }}>{lv.desc}</p></div></Reveal>)}</div>
      </section>

      {/* SIGNATURE */}
      <section className="nmh-glow" style={{ background: C.card2, borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}` }}><div style={sectionPad}><Reveal><div style={{ textAlign: "center", marginBottom: "64px" }}><span style={labelStyle}>{t.sigBlock.label}</span><h2 style={{ fontSize: "clamp(26px, 4vw, 44px)", fontWeight: 300 }}>{t.sigBlock.title}</h2></div></Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px" }}>{PRODUCTS.signature.map((p, i) => <ProdCard key={p.id} prod={p} delay={i * .05} lang={lang} onClick={goProd} />)}</div></div></section>

      {/* PRIVATE EDITIONS */}
      <section style={sectionPad}><Reveal><div style={{ textAlign: "center", marginBottom: "64px" }}><span style={labelStyle}>{t.privateBlock.label}</span><h2 style={{ fontSize: "clamp(26px, 4vw, 44px)", fontWeight: 300, marginBottom: "14px" }}>{t.privateBlock.title}</h2></div></Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "20px" }}>{PRODUCTS.privateEditions.map((p, i) => <ProdCard key={p.id} prod={p} delay={i * .06} showCode lang={lang} onClick={goProd} />)}</div></section>

      {/* RITUAL */}
      <section className="nmh-glow" style={{ background: C.card2, borderTop: `1px solid ${C.border}`, borderBottom: `1px solid ${C.border}` }}><div style={sectionPad}><Reveal><div style={{ textAlign: "center", marginBottom: "64px" }}><span style={labelStyle}>{t.ritualBlock.label}</span><h2 style={{ fontSize: "clamp(26px, 4vw, 44px)", fontWeight: 300 }}>{t.ritualBlock.title}</h2></div></Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px" }}>{PRODUCTS.ritualObjects.map((p, i) => <ProdCard key={p.id} prod={p} delay={i * .06} lang={lang} onClick={goProd} />)}</div></div></section>

      {/* JOURNAL */}
      <section style={sectionPad}><Reveal><div style={{ textAlign: "center", marginBottom: "56px" }}><span style={labelStyle}>{t.journal.label}</span><h2 style={{ fontSize: "clamp(26px, 4vw, 40px)", fontWeight: 300 }}>{t.journal.title}</h2></div></Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>{t.journal.articles.map((a, i) => <Reveal key={i} delay={i * .06}><div style={{ background: C.card, border: `1px solid ${C.border}`, padding: "36px 28px", cursor: "pointer", transition: "border-color .3s", height: "100%" }} onMouseEnter={e => e.currentTarget.style.borderColor = C.accentD} onMouseLeave={e => e.currentTarget.style.borderColor = C.border}><span style={{ fontFamily: C.sans, fontSize: "9px", letterSpacing: "3px", color: C.accent, display: "block", marginBottom: "16px" }}>{a.tag}</span><h3 style={{ fontSize: "22px", fontWeight: 300, marginBottom: "12px", lineHeight: 1.3 }}>{a.title}</h3><p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, lineHeight: 1.7 }}>{a.excerpt}</p></div></Reveal>)}</div></section>
    </>
  );

  const CatPage = ({ items, label, title, sub, showCode = false }) => (<section style={{ ...sectionPad, paddingTop: "150px" }}><Reveal><div style={{ textAlign: "center", marginBottom: "64px" }}><span style={labelStyle}>{label}</span><h1 style={{ fontSize: "clamp(30px, 5vw, 48px)", fontWeight: 300, marginBottom: "12px" }}>{title}</h1>{sub && <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, maxWidth: "520px", margin: "0 auto" }}>{sub}</p>}</div></Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "20px" }}>{items.map((p, i) => <ProdCard key={p.id} prod={p} delay={i * .05} showCode={showCode} lang={lang} onClick={goProd} />)}</div></section>);

  // PRODUCT PAGE
  const ProductPage = () => {
    const [selSz, setSelSz] = useState(0);
    const prod = selProd || PRODUCTS.signature[0];
    const isPE = prod.cat === "private";
    return (<section style={{ ...sectionPad, paddingTop: "130px" }}><Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "60px", alignItems: "start" }}>
      <NMHImage photoKey={prod.photo} name={prod.name} mode="product" style={{ border: `1px solid ${C.border}` }} />
      <div>
        {isPE && <span style={{ fontFamily: C.sans, fontSize: "9px", letterSpacing: "3px", color: C.muted, background: "rgba(201,169,110,.06)", padding: "4px 10px", border: `1px solid ${C.border}`, display: "inline-block", marginBottom: "14px" }}>{prod.type?.[lang]}</span>}
        <span style={labelStyle}>{prod.cat === "ritual" ? "Ritual Object" : "Eau de Parfum"}</span>
        <h1 style={{ fontSize: "clamp(32px, 5vw, 52px)", fontWeight: 300, letterSpacing: "2px", marginBottom: "8px" }}>{prod.name}</h1>
        {prod.code && <span style={{ fontFamily: C.sans, fontSize: "15px", color: C.accent, letterSpacing: "3px", display: "block", marginBottom: "10px" }}>{prod.code}</span>}
        <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, marginBottom: "4px" }}>{prod.desc[lang]}</p>
        <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.muted, fontStyle: "italic", marginBottom: "28px" }}>{prod.mood[lang]}</p>
        <p style={{ fontSize: "30px", fontWeight: 300, marginBottom: "28px" }}>${getPrice(prod.id, prod.sizes[selSz])}</p>

        <div style={{ marginBottom: "24px" }}><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "8px" }}>{t.product.volume}</span><div style={{ display: "flex", gap: "8px" }}>{prod.sizes.map((s, i) => <button key={i} onClick={() => setSelSz(i)} style={{ padding: "9px 22px", fontFamily: C.sans, fontSize: "12px", cursor: "pointer", background: selSz === i ? C.accent : "transparent", color: selSz === i ? C.bg : C.text, border: `1px solid ${selSz === i ? C.accent : C.border}`, transition: "all .2s" }}>{s}</button>)}</div></div>

        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", marginBottom: "28px" }}>
          <button className="nmh-btn-p" style={btnPrimary()} onClick={() => addCart(prod, prod.sizes[selSz])}>{t.product.addToCart}</button>
          <button style={btnOutline()} onClick={() => { addCart(prod, prod.sizes[selSz]); go("cart"); }}>{t.product.buyNow}</button>
        </div>

        <div style={{ padding: "16px", background: C.card, border: `1px solid ${C.border}`, marginBottom: "28px" }}>
          <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, marginBottom: "4px" }}>✦ {t.product.dispatch}</p>
          <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, marginBottom: "4px" }}>✦ {t.product.shippingNote} ${shipping.freeAbove}</p>
          <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec }}>✦ {t.product.returns}</p>
        </div>

        {prod.top && <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: "24px" }}>{[["topNotes", prod.top], ["heartNotes", prod.heart], ["baseNotes", prod.base]].map(([k, v]) => <div key={k} style={{ marginBottom: "16px" }}><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.accent, display: "block", marginBottom: "4px" }}>{t.product[k]}</span><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{v}</span></div>)}</div>}

        {isPE && <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: "24px", marginTop: "10px" }}><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.accent, display: "block", marginBottom: "14px" }}>{t.product.editionIdentity}</span>
          {[[t.product.editionType, prod.type?.[lang]], [t.product.releaseCode, prod.code], [t.product.unitsProduced, prod.units + " units"], [t.product.archiveStatus, prod.archiveStatus?.[lang]]].filter(([, v]) => v).map(([k, v]) => <div key={k} style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px", paddingBottom: "8px", borderBottom: `1px solid rgba(26,26,26,.5)` }}><span style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted }}>{k}</span><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{v}</span></div>)}
          {prod.collectorNote && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec, fontStyle: "italic", marginTop: "12px", padding: "12px", background: "rgba(201,169,110,.03)", border: `1px solid ${C.border}` }}>{prod.collectorNote[lang]}</p>}
        </div>}

        {prod.wear && <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: "24px", marginTop: "10px" }}><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.accent, display: "block", marginBottom: "12px" }}>{t.product.howItWears}</span>{[[t.product.intensity, prod.wear.i], [t.product.season, prod.wear.s], [t.product.longevity, prod.wear.l]].map(([k, v]) => <div key={k} style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", paddingBottom: "6px", borderBottom: `1px solid rgba(26,26,26,.4)` }}><span style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted }}>{k}</span><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{v}</span></div>)}</div>}
      </div>
    </div></Reveal>
    {prod.story && <Reveal><div style={{ marginTop: "80px", maxWidth: "680px", borderTop: `1px solid ${C.border}`, paddingTop: "36px" }}><span style={labelStyle}>{t.product.story}</span><p style={{ fontFamily: C.sans, fontSize: "14px", color: C.sec, lineHeight: 2 }}>{prod.story[lang]}</p></div></Reveal>}
    </section>);
  };

  // CART
  const CartPage = () => (<section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "760px" }}>
    <h1 style={{ fontSize: "32px", fontWeight: 300, marginBottom: "40px" }}>{t.cart.title}</h1>
    {cart.length === 0 ? (<div style={{ textAlign: "center", padding: "60px 0" }}><p style={{ fontFamily: C.sans, fontSize: "14px", color: C.sec, marginBottom: "28px" }}>{t.cart.empty}</p><button style={btnOutline()} onClick={() => go("signature")}>{t.cart.cont}</button></div>) : (<>
      {cart.map(it => <div key={it.cid} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "18px 0", borderBottom: `1px solid ${C.border}`, flexWrap: "wrap", gap: "10px" }}>
        <div><h3 style={{ fontSize: "17px", fontWeight: 300 }}>{it.name}{it.code ? ` ${it.code}` : ""}</h3><span style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted }}>{it.selectedSize}</span></div>
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <button onClick={() => updateQty(it.cid, it.qty - 1)} style={{ width: "26px", height: "26px", background: C.card, border: `1px solid ${C.border}`, color: C.text, cursor: "pointer", fontSize: "13px" }}>−</button>
            <span style={{ fontFamily: C.sans, fontSize: "13px", width: "20px", textAlign: "center" }}>{it.qty}</span>
            <button onClick={() => updateQty(it.cid, it.qty + 1)} style={{ width: "26px", height: "26px", background: C.card, border: `1px solid ${C.border}`, color: C.text, cursor: "pointer", fontSize: "13px" }}>+</button>
          </div>
          <span style={{ fontFamily: C.sans, fontSize: "14px", minWidth: "55px", textAlign: "right" }}>${it.price * it.qty}</span>
          <span onClick={() => rmCart(it.cid)} style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "1px", textTransform: "uppercase", color: C.muted, cursor: "pointer" }}>{t.cart.remove}</span>
        </div>
      </div>)}
      <div style={{ padding: "20px 0" }}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{t.cart.subtotal}</span><span style={{ fontFamily: C.sans, fontSize: "14px" }}>${subtotal}</span></div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{t.cart.shipping}</span><span style={{ fontFamily: C.sans, fontSize: "14px" }}>{shippingCost === 0 ? t.cart.free : `$${shippingCost}`}</span></div>
        <div style={{ display: "flex", justifyContent: "space-between", borderTop: `1px solid ${C.border}`, paddingTop: "14px", marginTop: "8px" }}><span style={{ fontFamily: C.sans, fontSize: "13px", fontWeight: 600 }}>{t.cart.total}</span><span style={{ fontSize: "22px", fontWeight: 300 }}>${total}</span></div>
      </div>
      <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}><button className="nmh-btn-p" style={btnPrimary()} onClick={() => go("checkout")}>{t.cart.checkout}</button><button style={btnOutline()} onClick={() => go("signature")}>{t.cart.cont}</button></div>
    </>)}
  </section>);

  // Checkout multi step flow
  const CheckoutPage = () => {
    const [step, setStep] = useState(0);
    const [form, setForm] = useState(() => { try { return JSON.parse(sessionStorage.getItem('nmh_co')) || {}; } catch { return {}; } });
    useEffect(() => { if (user && !form.name) setForm(f => ({ email: user.email, name: user.name, address: user.address, city: user.city, country: user.country, zip: user.zip, ...f })); }, [user]);
    const [selCurr, setSelCurr] = useState(null);
    const [payData, setPayData] = useState(null);
    const [err, setErr] = useState(null);
    const [copied, setCopied] = useState(false);
    const [orderId, setOrderId] = useState(null);
    const [agreed, setAgreed] = useState(false);
    const [timer, setTimer] = useState(null);
    // Promo code
    const [promoInput, setPromoInput] = useState('');
    const [promoResult, setPromoResult] = useState(null); // {valid,code,discount} or null
    const [promoErr, setPromoErr] = useState(null);
    const promoDiscount = promoResult?.discount || 0;
    const checkoutTotal = Math.max(0, total - promoDiscount);

    useEffect(() => { sessionStorage.setItem('nmh_co', JSON.stringify(form)); }, [form]);
    useEffect(() => { if (step === 3 && payData) { const end = Date.now() + (payData.timeout || 60) * 60000; const iv = setInterval(() => { const r = Math.max(0, Math.floor((end - Date.now()) / 1000)); setTimer(r); if (r <= 0) clearInterval(iv); }, 1000); return () => clearInterval(iv); } }, [step, payData]);
    const upd = (k, v) => setForm(f => ({ ...f, [k]: v }));
    const currencies = storeConfig?.currencies || [];
    const fmtT = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

    const applyPromo = async () => {
      if (!promoInput.trim()) return;
      setPromoErr(null);
      try {
        const r = await fetch('/api/promo/validate', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: promoInput, items: cart.map(i => ({ id: i.id, size: i.selectedSize, qty: i.qty })) }) });
        const d = await r.json();
        if (d.error) {
          setPromoErr(d.error === 'invalid' ? (lang === 'ru' ? 'Код не найден' : lang === 'es' ? 'Codigo invalido' : 'Invalid code') :
            d.error === 'not_applicable' ? (lang === 'ru' ? 'Код не применим к товарам в корзине' : lang === 'es' ? 'No aplicable' : 'Not applicable to your items') : d.error);
          setPromoResult(null);
        } else { setPromoResult(d); setPromoErr(null); }
      } catch { setPromoErr('Error'); }
    };

    const submitInfo = async () => {
      if (!form.email || !form.name || !agreed) { setErr("Fill all fields"); return; }
      setErr(null); setStep(-1);
      try {
        const r = await fetch('/api/orders', { method: 'POST', headers: authHeaders,
          body: JSON.stringify({ ...form, lang, promoCode: promoResult?.code || '', items: cart.map(i => ({ id: i.id, code: i.code || '', size: i.selectedSize, qty: i.qty })) }) });
        const d = await r.json(); if (d.error) throw new Error(d.error);
        setOrderId(d.orderId); setStep(1);
      } catch (e) { setErr(e.message); setStep(0); }
    };
    const selectCurrency = (c) => { setSelCurr(c); if (!c.networks) submitPay(c.code, null); else setStep(2); };
    const submitPay = async (cur, net) => {
      setStep(-1); setErr(null);
      try { const r = await fetch(`/api/orders/${orderId}/pay`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ currency: cur, network: net }) }); const d = await r.json(); if (d.error) throw new Error(d.error); setPayData(d); setStep(3); } catch (e) { setErr(e.message); setStep(1); }
    };

    if (step === -1) return <section style={{ ...sectionPad, paddingTop: "200px", textAlign: "center" }}><div style={{ width: "36px", height: "36px", border: `2px solid ${C.accent}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin 1s linear infinite", margin: "0 auto 24px" }} /><p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec }}>{t.checkout.processing}</p></section>;

    if (step === 4) return <section style={{ ...sectionPad, paddingTop: "200px", textAlign: "center", maxWidth: "560px" }}><div style={{ fontSize: "40px", color: C.accent, marginBottom: "20px" }}>✦</div><h1 style={{ fontSize: "32px", fontWeight: 300, marginBottom: "12px" }}>{t.checkout.orderConfirmed}</h1><p style={{ fontFamily: C.sans, fontSize: "14px", color: C.sec, marginBottom: "6px" }}>{t.checkout.orderSuccess}</p><p style={{ fontFamily: C.sans, fontSize: "15px", color: C.accent, marginBottom: "36px" }}>{orderId}</p><button style={btnPrimary()} onClick={() => { go("home"); setCart([]); }}>{t.checkout.backHome}</button></section>;

    if (step === 3 && payData) return <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "560px" }}>
      <h1 style={{ fontSize: "28px", fontWeight: 300, marginBottom: "32px" }}>{t.checkout.paymentDetails}</h1>
      <div style={{ background: C.card, border: `1px solid ${C.border}`, padding: "32px" }}>
        <div style={{ textAlign: "center", marginBottom: "24px" }}><p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, marginBottom: "6px" }}>{t.checkout.sendExactly}</p><p style={{ fontSize: "32px", fontWeight: 300, color: C.accent, marginBottom: "6px" }}>${payData.total}</p><p style={{ fontFamily: C.sans, fontSize: "13px" }}>{payData.currency}{payData.network ? `: ${payData.network}` : ""}</p></div>
        {payData.qrCode && <div style={{ display: "flex", justifyContent: "center", marginBottom: "20px" }}><img src={payData.qrCode} alt="QR" loading="lazy" style={{ width: "180px", height: "180px" }} /></div>}
        <div style={{ background: C.bg, border: `1px solid ${C.border}`, padding: "14px", marginBottom: "14px" }}>
          <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.text, wordBreak: "break-all", marginBottom: "10px" }}>{payData.address}</p>
          <button onClick={() => { navigator.clipboard.writeText(payData.address); setCopied(true); setTimeout(() => setCopied(false), 1500); }} style={{ ...btnPrimary({ padding: "7px 16px", fontSize: "9px" }), background: copied ? C.green : C.accent }}>{copied ? t.checkout.copied : t.checkout.copyAddress}</button>
        </div>
        <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.red, marginBottom: "20px" }}>{t.checkout.wrongNetwork}</p>
        {timer !== null && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.muted, textAlign: "center", marginBottom: "16px" }}>{t.checkout.timeRemaining}: <span style={{ color: timer < 300 ? C.red : C.accent }}>{fmtT(timer)}</span></p>}
        <div style={{ textAlign: "center", padding: "14px", background: "rgba(201,169,110,.03)", border: `1px solid ${C.border}` }}><p style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{t.checkout.waitingPayment}</p></div>
      </div>
      <div style={{marginTop:"24px",textAlign:"center"}}>
        <button className="nmh-btn-p" style={btnPrimary({width:"100%",padding:"16px"})} onClick={async()=>{
          try{await fetch(`/api/orders/${payData.orderId}/payment-sent`,{method:'POST',headers:{'Content-Type':'application/json'}});setStep(5);}catch{setStep(5);}
        }}>{lang==='ru'?'Я отправил оплату':lang==='es'?'He enviado el pago':'I\'ve Sent the Payment'}</button>
      </div>
    </section>;

    // Step 5: Awaiting confirmation
    if(step===5)return<section style={{...sectionPad,paddingTop:"200px",textAlign:"center",maxWidth:"560px"}}>
      <div style={{fontSize:"40px",color:C.accent,marginBottom:"20px"}}>◆</div>
      <h1 style={{fontSize:"28px",fontWeight:300,marginBottom:"12px"}}>{lang==='ru'?'Заказ принят':lang==='es'?'Pedido recibido':'Order Received'}</h1>
      <p style={{fontFamily:C.sans,fontSize:"14px",color:C.sec,lineHeight:1.9,marginBottom:"8px"}}>{lang==='ru'?'Мы проверим вашу оплату и отправим подтверждение на email.':lang==='es'?'Verificaremos su pago y enviaremos confirmación por email.':'We are verifying your payment. A confirmation email will be sent once confirmed.'}</p>
      <p style={{fontFamily:C.sans,fontSize:"15px",color:C.accent,marginBottom:"36px"}}>{orderId}</p>
      <div style={{display:"flex",gap:"14px",justifyContent:"center",flexWrap:"wrap"}}>
        <button className="nmh-btn-p" style={btnPrimary()} onClick={()=>{go("home");setCart([])}}>{t.checkout.backHome}</button>
        <button className="nmh-btn-o" style={btnOutline()} onClick={()=>go("orderStatus")}>{t.checkout.trackOrder}</button>
      </div>
    </section>;

    if (step === 2 && selCurr) return <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "560px" }}>
      <h1 style={{ fontSize: "28px", fontWeight: 300, marginBottom: "12px" }}>{t.checkout.selectNetwork}</h1>
      <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, marginBottom: "32px" }}>{selCurr.name}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>{selCurr.networks.map(n => <button key={n.id} onClick={() => submitPay(selCurr.code, n.id)} style={{ padding: "18px 20px", fontFamily: C.sans, fontSize: "14px", background: C.card, border: `1px solid ${C.border}`, color: C.text, cursor: "pointer", textAlign: "left", transition: "border-color .2s", display: "flex", justifyContent: "space-between" }} onMouseEnter={e => e.currentTarget.style.borderColor = C.accent} onMouseLeave={e => e.currentTarget.style.borderColor = C.border}><span>{n.name}</span><span style={{ color: C.accent }}>→</span></button>)}</div>
    </section>;

    if (step === 1) return <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "560px" }}>
      <h1 style={{ fontSize: "28px", fontWeight: 300, marginBottom: "12px" }}>{t.checkout.selectCurrency}</h1>
      <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, marginBottom: "32px" }}>{t.checkout.orderNumber}: <span style={{ color: C.accent }}>{orderId}</span>: ${total}</p>
      {err && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.red, marginBottom: "12px" }}>{err}</p>}
      {currencies.length === 0 ? <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.muted }}>No payment methods configured.</p> :
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "10px" }}>{currencies.map(c => <button key={c.code} onClick={() => selectCurrency(c)} style={{ padding: "20px 12px", fontFamily: C.sans, fontSize: "14px", fontWeight: 500, background: C.card, border: `1px solid ${C.border}`, color: C.text, cursor: "pointer", transition: "border-color .2s", textAlign: "center" }} onMouseEnter={e => e.currentTarget.style.borderColor = C.accent} onMouseLeave={e => e.currentTarget.style.borderColor = C.border}><div style={{ fontSize: "16px", marginBottom: "4px" }}>{c.code}</div><div style={{ fontSize: "9px", color: C.muted }}>{c.name}</div></button>)}</div>}
    </section>;

    return <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "660px" }}>
      <h1 style={{ fontSize: "32px", fontWeight: 300, marginBottom: "40px" }}>{t.checkout.title}</h1>
      {err && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.red, marginBottom: "14px" }}>{err}</p>}
      <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
        <div><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "6px" }}>{t.checkout.email}</label><input style={inputStyle} type="email" value={form.email || ""} onChange={e => upd('email', e.target.value)} onFocus={e => e.target.style.borderColor = C.accent} onBlur={e => e.target.style.borderColor = C.border} /></div>
        <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: "20px" }}><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.accent, display: "block", marginBottom: "16px" }}>{t.checkout.shipping}</span></div>
        {["name", "address", "city", "country", "zip"].map(f => <div key={f}><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "6px" }}>{t.checkout[f]}</label><input style={inputStyle} value={form[f] || ""} onChange={e => upd(f, e.target.value)} onFocus={e => e.target.style.borderColor = C.accent} onBlur={e => e.target.style.borderColor = C.border} /></div>)}
        <div style={{ padding: "20px", background: C.card, border: `1px solid ${C.border}` }}>
          {cart.map(it => <div key={it.cid} style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{it.name} × {it.qty}</span><span style={{ fontFamily: C.sans, fontSize: "12px" }}>${it.price * it.qty}</span></div>)}
          <div style={{ borderTop: `1px solid ${C.border}`, marginTop: "10px", paddingTop: "10px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{t.cart.subtotal}</span><span style={{ fontFamily: C.sans, fontSize: "12px" }}>${subtotal}</span></div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{t.cart.shipping}</span><span style={{ fontFamily: C.sans, fontSize: "12px" }}>{shippingCost === 0 ? t.cart.free : `$${shippingCost}`}</span></div>
            {promoDiscount > 0 && <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.accent }}>{lang === 'ru' ? 'Промокод' : 'Promo'} ({promoResult.code})</span><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.accent }}>{lang === 'ru' ? `Скидка $${promoDiscount}` : `Discount $${promoDiscount}`}</span></div>}
            <div style={{ display: "flex", justifyContent: "space-between", borderTop: `1px solid ${C.border}`, paddingTop: "8px", marginTop: "4px" }}><span style={{ fontFamily: C.sans, fontSize: "13px", fontWeight: 600 }}>{t.cart.total}</span><span style={{ fontSize: "18px", fontWeight: 300 }}>${checkoutTotal}</span></div>
          </div>

          {/* Promo code input */}
          <div style={{ padding: "16px", background: "rgba(201,169,110,.02)", border: `1px solid ${C.border}` }}>
            <div style={{ display: "flex", gap: "8px" }}>
              <input style={{ ...inputStyle, flex: 1, fontSize: "12px", padding: "10px 14px", letterSpacing: "2px", textTransform: "uppercase" }} placeholder={lang === 'ru' ? 'Промокод' : lang === 'es' ? 'Codigo' : 'Promo code'} value={promoInput} onChange={e => setPromoInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && applyPromo()} />
              <button onClick={applyPromo} style={{ padding: "10px 20px", fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", background: "transparent", color: C.accent, border: `1px solid ${C.accent}`, cursor: "pointer", transition: "all .3s", whiteSpace: "nowrap" }}>{lang === 'ru' ? 'Применить' : lang === 'es' ? 'Aplicar' : 'Apply'}</button>
            </div>
            {promoErr && <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.red, marginTop: "8px" }}>{promoErr}</p>}
            {promoResult && <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.accent, marginTop: "8px" }}>{PROMO_CODES[promoResult.code]?.description?.[lang] || `Discount: $${promoResult.discount}`}</p>}
          </div>
        </div>
        <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontFamily: C.sans, fontSize: "12px", color: C.sec }}><input type="checkbox" checked={agreed} onChange={e => setAgreed(e.target.checked)} style={{ accentColor: C.accent }} />{t.checkout.agree}</label>
        <button style={{ ...btnPrimary({ width: "100%", padding: "16px" }), opacity: agreed ? 1 : 0.4 }} onClick={submitInfo} disabled={!agreed}>{t.checkout.proceed}</button>
      </div>
    </section>;
  };

  // SUPPORT
  const SupportPage = () => {
    const support = storeConfig?.support || {};
    const [cf, setCf] = useState({}); const [st, setSt] = useState(null);
    const send = async () => { setSt('sending'); try { const r = await fetch('/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...cf, lang }) }); if (r.ok) { setSt('sent'); setCf({}); } else setSt('error'); } catch { setSt('error'); } };
    return <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "760px" }}>
      <Reveal><span style={labelStyle}>{t.support.title}</span><h1 style={{ fontSize: "clamp(28px, 5vw, 44px)", fontWeight: 300, marginBottom: "14px" }}>{t.support.title}</h1><p style={{ fontFamily: C.sans, fontSize: "14px", color: C.sec, marginBottom: "56px" }}>{t.support.sub}</p></Reveal>
      <Reveal delay={.08}><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", marginBottom: "64px" }}>
        {[["Instagram", support.instagram, NmhIconInstagram], ["Telegram", support.telegram, NmhIconTelegram], ["WhatsApp", support.whatsapp, NmhIconWhatsApp], ["Email", support.email ? "mailto:" + support.email : "", NmhIconEmail]].filter(([, u]) => u).map(([n, u, Icon]) => <a key={n} href={u} target="_blank" rel="noopener" style={{ display: "flex", alignItems: "center", gap: "14px", background: C.card, border: `1px solid ${C.border}`, padding: "22px 24px", textDecoration: "none", color: C.text, transition: "border-color .3s, transform .3s" }} onMouseEnter={e => {e.currentTarget.style.borderColor = C.accent; e.currentTarget.style.transform = "translateY(-2px)";}} onMouseLeave={e => {e.currentTarget.style.borderColor = C.border; e.currentTarget.style.transform = "none";}}><Icon size={22} /><span style={{ fontFamily: C.sans, fontSize: "13px", letterSpacing: "1px" }}>{n}</span></a>)}
      </div></Reveal>
      <Reveal delay={.12}><h2 style={{ fontSize: "24px", fontWeight: 300, marginBottom: "28px" }}>{t.support.contactForm}</h2>
        {st === 'sent' ? <div style={{ padding: "32px", background: C.card, border: `1px solid ${C.green}`, textAlign: "center" }}><p style={{ fontFamily: C.sans, fontSize: "14px", color: C.green }}>{t.support.formSent}</p></div> : <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {[["formName", "name", "text"], ["formEmail", "email", "email"], ["formSubject", "subject", "text"]].map(([l, k, ty]) => <div key={k}><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "6px" }}>{t.support[l]}</label><input style={inputStyle} type={ty} value={cf[k] || ""} onChange={e => setCf(f => ({ ...f, [k]: e.target.value }))} /></div>)}
          <div><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "6px" }}>{t.support.formMessage}</label><textarea style={{ ...inputStyle, height: "100px", resize: "vertical" }} value={cf.message || ""} onChange={e => setCf(f => ({ ...f, message: e.target.value }))} /></div>
          <div><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "6px" }}>{t.support.formTelegram}</label><input style={inputStyle} value={cf.telegram || ""} onChange={e => setCf(f => ({ ...f, telegram: e.target.value }))} /></div>
          {st === 'error' && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.red }}>{t.support.formError}</p>}
          <button style={btnPrimary({ width: "100%", padding: "14px" })} onClick={send}>{t.support.formSend}</button>
        </div>}
      </Reveal>
    </section>;
  };

  const AboutPage = () => <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "760px" }}><Reveal><span style={labelStyle}>{t.houseSection.label}</span><h1 style={{ fontSize: "clamp(28px, 5vw, 48px)", fontWeight: 300, marginBottom: "40px" }}>{t.houseSection.title}</h1><p style={{ fontFamily: C.sans, fontSize: "15px", color: C.sec, lineHeight: 2, marginBottom: "18px" }}>{t.houseSection.p1}</p><p style={{ fontFamily: C.sans, fontSize: "15px", color: C.sec, lineHeight: 2, marginBottom: "18px" }}>{t.houseSection.p2}</p><p style={{ fontFamily: C.sans, fontSize: "15px", color: C.sec, lineHeight: 2 }}>{t.houseSection.p3}</p></Reveal></section>;

  const FaqPage = () => <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "760px" }}><Reveal><span style={labelStyle}>{t.faq.label}</span><h1 style={{ fontSize: "clamp(28px, 5vw, 44px)", fontWeight: 300, marginBottom: "48px" }}>{t.faq.title}</h1></Reveal>{t.faq.items.map((it, i) => <div key={i} style={{ borderBottom: `1px solid ${C.border}` }}><div onClick={() => setOpenFaq(openFaq === i ? null : i)} style={{ padding: "20px 0", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center", gap: "16px" }}><span style={{ fontFamily: C.sans, fontSize: "13px", lineHeight: 1.5 }}>{it.q}</span><span style={{ color: C.accent, fontSize: "16px", transition: "transform .2s", transform: openFaq === i ? "rotate(45deg)" : "", flexShrink: 0 }}>+</span></div><div style={{ maxHeight: openFaq === i ? "300px" : "0", overflow: "hidden", transition: "max-height .3s ease" }}><p style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec, lineHeight: 1.8, paddingBottom: "20px" }}>{it.a}</p></div></div>)}</section>;

  const JournalPage = () => <section style={{ ...sectionPad, paddingTop: "150px" }}><Reveal><span style={labelStyle}>{t.journal.label}</span><h1 style={{ fontSize: "clamp(28px, 5vw, 44px)", fontWeight: 300, marginBottom: "48px" }}>{t.journal.title}</h1></Reveal><div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>{t.journal.articles.map((a, i) => <Reveal key={i} delay={i * .06}><div style={{ background: C.card, border: `1px solid ${C.border}`, padding: "36px 28px", height: "100%" }}><span style={{ fontFamily: C.sans, fontSize: "9px", letterSpacing: "3px", color: C.accent, display: "block", marginBottom: "16px" }}>{a.tag}</span><h3 style={{ fontSize: "22px", fontWeight: 300, marginBottom: "12px", lineHeight: 1.3 }}>{a.title}</h3><p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, lineHeight: 1.7 }}>{a.excerpt}</p></div></Reveal>)}</div></section>;

  const OrderStatusPage = () => {
    const [oid, setOid] = useState(''); const [order, setOrder] = useState(null); const [err, setErr] = useState(null);
    const lookup = async () => { try { const r = await fetch(`/api/orders/${oid}`); const d = await r.json(); if (d.error) throw new Error(d.error); setOrder(d); setErr(null); } catch (e) { setErr(e.message); } };
    return <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "560px" }}><h1 style={{ fontSize: "28px", fontWeight: 300, marginBottom: "32px" }}>{t.orderStatus.title}</h1><div style={{ display: "flex", gap: "10px", marginBottom: "28px" }}><input style={{ ...inputStyle, flex: 1 }} placeholder={t.orderStatus.orderId} value={oid} onChange={e => setOid(e.target.value)} onKeyDown={e => e.key === 'Enter' && lookup()} /><button style={btnPrimary({ padding: "12px 24px" })} onClick={lookup}>→</button></div>
      {err && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.red, marginBottom: "12px" }}>{err}</p>}
      {order && <div style={{ background: C.card, border: `1px solid ${C.border}`, padding: "28px" }}>{[[t.orderStatus.orderId, order.id], [t.orderStatus.status, t.orderStatus.statuses[order.status] || order.status], [t.cart.total, `$${order.total}`]].map(([k, v]) => <div key={k} style={{ display: "flex", justifyContent: "space-between", marginBottom: "14px" }}><span style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>{k}</span><span style={{ fontFamily: C.sans, fontSize: "14px", color: C.accent }}>{v}</span></div>)}{order.tracking_number && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.sec }}>Tracking: {order.tracking_number}</p>}</div>}
    </section>;
  };

  // ACCOUNT PAGE Login, register, profile, and order history
  const AccountPage = () => {
    const [mode, setMode] = useState(user ? 'profile' : 'login');
    const [af, setAf] = useState({});
    const [err, setErr] = useState(null);
    const [orders, setOrders] = useState([]);
    const [profileSaved, setProfileSaved] = useState(false);

    // Load orders when logged in
    useEffect(() => {
      if (user && authToken) {
        fetch('/api/auth/orders', { headers: { 'x-auth-token': authToken } })
          .then(r => r.json()).then(setOrders).catch(() => {});
      }
    }, [user, authToken]);

    // Prefill profile from user data
    useEffect(() => { if (user) setAf({ name: user.name, address: user.address, city: user.city, country: user.country, zip: user.zip }); }, [user]);

    const doAuth = async (endpoint) => {
      setErr(null);
      try {
        const r = await fetch(`/api/auth/${endpoint}`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: af.email, password: af.password, name: af.name, lang }) });
        const d = await r.json();
        if (d.error) throw new Error(d.error);
        setAuthToken(d.token); setUser(d.user); setMode('profile');
      } catch (e) { setErr(e.message); }
    };

    const saveProfile = async () => {
      try {
        await fetch('/api/auth/me', { method: 'PATCH', headers: authHeaders, body: JSON.stringify(af) });
        setProfileSaved(true); setTimeout(() => setProfileSaved(false), 2000);
      } catch {}
    };

    // Profile view (logged in)
    if (user) return (
      <section style={{ ...sectionPad, paddingTop: "150px", maxWidth: "700px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "40px" }}>
          <div>
            <span style={labelStyle}>{lang === 'ru' ? 'Личный кабинет' : lang === 'es' ? 'Mi cuenta' : 'My Account'}</span>
            <h1 style={{ fontSize: "28px", fontWeight: 300 }}>{user.name || user.email}</h1>
          </div>
          <span onClick={logout} style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, cursor: "pointer" }}>{lang === 'ru' ? 'Выйти' : lang === 'es' ? 'Salir' : 'Logout'}</span>
        </div>

        {/* Saved address */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, padding: "28px", marginBottom: "40px" }}>
          <h3 style={{ fontFamily: C.sans, fontSize: "11px", letterSpacing: "3px", textTransform: "uppercase", color: C.accent, marginBottom: "18px" }}>{lang === 'ru' ? 'Адрес доставки' : lang === 'es' ? 'Dirección' : 'Shipping Address'}</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            {[["name", "Name"], ["address", "Address"], ["city", "City"], ["country", "Country"], ["zip", "Postal Code"]].map(([k, l]) => (
              <div key={k} style={k === "address" ? { gridColumn: "1/3" } : {}}>
                <label style={{ fontFamily: C.sans, fontSize: "9px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "4px" }}>{l}</label>
                <input style={inputStyle} value={af[k] || ""} onChange={e => setAf(f => ({ ...f, [k]: e.target.value }))} />
              </div>
            ))}
          </div>
          <button className="nmh-btn-p" style={btnPrimary({ marginTop: "16px", padding: "10px 28px", background: profileSaved ? C.green : C.accent })} onClick={saveProfile}>{profileSaved ? "✓" : (lang === 'ru' ? 'Сохранить' : lang === 'es' ? 'Guardar' : 'Save')}</button>
        </div>

        {/* Order history */}
        <h3 style={{ fontFamily: C.sans, fontSize: "11px", letterSpacing: "3px", textTransform: "uppercase", color: C.accent, marginBottom: "16px" }}>{lang === 'ru' ? 'История заказов' : lang === 'es' ? 'Historial' : 'Order History'}</h3>
        {orders.length === 0 ? <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.muted }}>{lang === 'ru' ? 'Заказов пока нет' : lang === 'es' ? 'Sin pedidos' : 'No orders yet'}</p> :
          orders.map(o => (
            <div key={o.id} style={{ background: C.card, border: `1px solid ${C.border}`, padding: "18px", marginBottom: "8px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
              <div>
                <span style={{ fontFamily: C.sans, fontSize: "14px", color: C.accent }}>{o.id}</span>
                <span style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted, marginLeft: "12px" }}>{new Date(o.created_at).toLocaleDateString()}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                <span style={{ fontFamily: C.sans, fontSize: "14px" }}>${o.total}</span>
                <span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "1px", textTransform: "uppercase", color: o.status === 'confirmed' ? C.green : C.sec }}>{t.orderStatus?.statuses?.[o.status] || o.status}</span>
              </div>
            </div>
          ))
        }
      </section>
    );

    // Login / Register form
    return (
      <section style={{ ...sectionPad, paddingTop: "180px", maxWidth: "420px", textAlign: "center" }}>
        <h1 style={{ fontSize: "28px", fontWeight: 300, marginBottom: "8px" }}>{mode === 'login' ? (lang === 'ru' ? 'Вход' : lang === 'es' ? 'Iniciar sesión' : 'Sign In') : (lang === 'ru' ? 'Регистрация' : lang === 'es' ? 'Registrarse' : 'Create Account')}</h1>
        <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, marginBottom: "32px" }}>{lang === 'ru' ? 'Ваш личный кабинет в Доме' : lang === 'es' ? 'Tu espacio personal en la Casa' : 'Your personal space in the House'}</p>
        {err && <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.red, marginBottom: "12px" }}>{err}</p>}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", textAlign: "left" }}>
          {mode === 'register' && <div><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "4px" }}>{lang === 'ru' ? 'Имя' : 'Name'}</label><input style={inputStyle} value={af.name || ""} onChange={e => setAf(f => ({ ...f, name: e.target.value }))} /></div>}
          <div><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "4px" }}>Email</label><input style={inputStyle} type="email" value={af.email || ""} onChange={e => setAf(f => ({ ...f, email: e.target.value }))} /></div>
          <div><label style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "2px", textTransform: "uppercase", color: C.muted, display: "block", marginBottom: "4px" }}>{lang === 'ru' ? 'Пароль' : 'Password'}</label><input style={inputStyle} type="password" value={af.password || ""} onChange={e => setAf(f => ({ ...f, password: e.target.value }))} onKeyDown={e => e.key === 'Enter' && doAuth(mode === 'login' ? 'login' : 'register')} /></div>
          <button className="nmh-btn-p" style={btnPrimary({ width: "100%", padding: "14px" })} onClick={() => doAuth(mode === 'login' ? 'login' : 'register')}>{mode === 'login' ? (lang === 'ru' ? 'Войти' : lang === 'es' ? 'Entrar' : 'Sign In') : (lang === 'ru' ? 'Создать' : lang === 'es' ? 'Crear' : 'Create')}</button>
          <p style={{ fontFamily: C.sans, fontSize: "12px", color: C.muted, textAlign: "center", marginTop: "8px" }}>
            {mode === 'login' ? (lang === 'ru' ? 'Нет аккаунта? ' : lang === 'es' ? '¿Sin cuenta? ' : 'No account? ') : (lang === 'ru' ? 'Есть аккаунт? ' : lang === 'es' ? '¿Ya tienes cuenta? ' : 'Have an account? ')}
            <span onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setErr(null); }} style={{ color: C.accent, cursor: "pointer" }}>{mode === 'login' ? (lang === 'ru' ? 'Создать' : lang === 'es' ? 'Crear' : 'Create one') : (lang === 'ru' ? 'Войти' : lang === 'es' ? 'Entrar' : 'Sign in')}</span>
          </p>
        </div>
      </section>
    );
  };


  // FRAGRANCE FINDER luxury quiz for undecided visitors
  const FragranceFinder = () => {
    const [step, setStep] = useState(0);
    const [answers, setAnswers] = useState([]);
    const questions = [
      { q: { en: "What is your character?", ru: "Какой вы по характеру?", es: "Tu caracter?" },
        opts: [
          { en: "Calm and reserved", ru: "Спокойный и сдержанный", es: "Tranquilo", tags: ['cr', 'vs'] },
          { en: "Confident and dominant", ru: "Уверенный и доминантный", es: "Dominante", tags: ['bl', 'nc'] },
          { en: "Elegant and refined", ru: "Элегантный и утончённый", es: "Elegante", tags: ['at', 'vs'] }
        ]},
      { q: { en: "When do you wear fragrance?", ru: "Когда вы носите аромат?", es: "Cuando usas fragancia?" },
        opts: [
          { en: "Evening and night", ru: "Вечер и ночь", es: "Noche", tags: ['nc', 'bl'] },
          { en: "All day", ru: "Весь день", es: "Todo el dia", tags: ['cr', 'at'] },
          { en: "Special occasions", ru: "Особые случаи", es: "Ocasiones", tags: ['nc43', 'fm'] }
        ]},
      { q: { en: "Your ideal atmosphere?", ru: "Ваша идеальная атмосфера?", es: "Tu atmosfera ideal?" },
        opts: [
          { en: "Cold minimalism", ru: "Холодный минимализм", es: "Minimalismo", tags: ['vs', 'cr'] },
          { en: "Warm luxury", ru: "Тёплая роскошь", es: "Lujo calido", tags: ['nc', 'bl'] },
          { en: "Clean sophistication", ru: "Чистая утончённость", es: "Sofisticacion", tags: ['at', 'vs'] }
        ]}
    ];

    const pickAnswer = (opt) => {
      const newAnswers = [...answers, opt.tags];
      setAnswers(newAnswers);
      if (step < questions.length - 1) setStep(step + 1);
      else setStep(99); // results
    };

    // Calculate result
    const getResult = () => {
      const scores = {};
      answers.flat().forEach(id => { scores[id] = (scores[id] || 0) + 1; });
      const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
      const topId = sorted[0]?.[0] || 'nc';
      const altId = sorted[1]?.[0] || 'cr';
      return {
        main: ALL_PRODUCTS.find(p => p.id === topId) || PRODUCTS.signature[0],
        alt: ALL_PRODUCTS.find(p => p.id === altId) || PRODUCTS.signature[1]
      };
    };

    const close = () => { setFinderActive(false); setShowFinder(false); setStep(0); setAnswers([]); };

    // Results screen
    if (step === 99) {
      const { main, alt } = getResult();
      return (
        <div style={{ position: "fixed", inset: 0, zIndex: 3000, background: "rgba(10,10,10,.95)", display: "flex", alignItems: "center", justifyContent: "center", padding: "24px" }}>
          <div style={{ maxWidth: "500px", width: "100%", textAlign: "center" }}>
            <span style={labelStyle}>{lang === 'ru' ? 'Ваш аромат' : lang === 'es' ? 'Tu aroma' : 'Your Scent'}</span>
            <h2 style={{ fontSize: "32px", fontWeight: 300, marginBottom: "8px" }}>{main.name}</h2>
            {main.code && <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.accent, marginBottom: "8px" }}>{main.code}</p>}
            <p style={{ fontFamily: C.sans, fontSize: "13px", color: C.sec, marginBottom: "24px", lineHeight: 1.7 }}>{main.desc?.[lang] || main.desc?.en}</p>
            <NMHImage photoKey={main.photo} name={main.name} mode="card" height="240px" style={{ marginBottom: "24px", border: `1px solid ${C.border}` }} />
            <div style={{ display: "flex", gap: "10px", justifyContent: "center", flexWrap: "wrap", marginBottom: "32px" }}>
              <button className="nmh-btn-p" style={btnPrimary()} onClick={() => { goProd(main); close(); }}>{lang === 'ru' ? 'Подробнее' : lang === 'es' ? 'Ver mas' : 'View Product'}</button>
              <button style={btnOutline()} onClick={() => { addCart(main, main.sizes[0]); close(); }}>{t.product.addToCart}</button>
            </div>
            {alt && <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted, cursor: "pointer" }} onClick={() => { goProd(alt); close(); }}>{lang === 'ru' ? 'Также подойдёт' : 'Also recommended'}: <span style={{ color: C.accent }}>{alt.name}</span></p>}
            <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted, marginTop: "24px", cursor: "pointer" }} onClick={close}>{lang === 'ru' ? 'Закрыть' : 'Close'}</p>
          </div>
        </div>
      );
    }

    // Quiz screen
    const q = questions[step];
    return (
      <div style={{ position: "fixed", inset: 0, zIndex: 3000, background: "rgba(10,10,10,.95)", display: "flex", alignItems: "center", justifyContent: "center", padding: "24px" }}>
        <div style={{ maxWidth: "480px", width: "100%", textAlign: "center" }}>
          <span style={{ ...labelStyle, marginBottom: "24px" }}>{step + 1} / {questions.length}</span>
          <h2 style={{ fontSize: "26px", fontWeight: 300, marginBottom: "40px", lineHeight: 1.3 }}>{q.q[lang] || q.q.en}</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {q.opts.map((opt, i) => (
              <button key={i} onClick={() => pickAnswer(opt)} style={{ padding: "20px 24px", fontFamily: C.sans, fontSize: "14px", background: C.card, border: `1px solid ${C.border}`, color: C.text, cursor: "pointer", transition: "all .3s", textAlign: "center" }} onMouseEnter={e => e.currentTarget.style.borderColor = C.accent} onMouseLeave={e => e.currentTarget.style.borderColor = C.border}>{opt[lang] || opt.en}</button>
            ))}
          </div>
          <p style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted, marginTop: "24px", cursor: "pointer" }} onClick={close}>{lang === 'ru' ? 'Закрыть' : 'Close'}</p>
        </div>
      </div>
    );
  };

  // FOOTER
  const Footer = () => {
    const support = storeConfig?.support || {};
    return <footer style={{ borderTop: `1px solid ${C.border}`, marginTop: "80px" }}><div style={{ maxWidth: "1200px", margin: "0 auto", padding: "72px 24px 32px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "40px", marginBottom: "56px" }}>
        <div><span style={{ fontSize: "20px", fontWeight: 300, letterSpacing: "8px", textTransform: "uppercase", display: "block", marginBottom: "14px" }}>NMH</span><p style={{ fontFamily: C.sans, fontSize: "11px", color: C.muted, lineHeight: 1.8, fontStyle: "italic" }}>{t.footer.tagline}</p></div>
        <div><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", color: C.accent, display: "block", marginBottom: "14px" }}>Collection</span>{["Signature", "Initiation", "Private Editions", "Ritual Objects"].map(s => <span key={s} onClick={() => go(s.toLowerCase().replace(/ /g, '').replace('privateeditions', 'private').replace('ritualobjects', 'ritual'))} style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, display: "block", marginBottom: "8px", cursor: "pointer" }}>{s}</span>)}</div>
        <div><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", color: C.accent, display: "block", marginBottom: "14px" }}>Support</span><span onClick={() => go("support")} style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, display: "block", marginBottom: "8px", cursor: "pointer" }}>{t.nav.support}</span><span onClick={() => go("faq")} style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, display: "block", marginBottom: "8px", cursor: "pointer" }}>FAQ</span><span onClick={() => go("orderStatus")} style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, display: "block", marginBottom: "8px", cursor: "pointer" }}>{t.orderStatus.title}</span>
          <div style={{ display: "flex", gap: "10px", marginTop: "12px" }}>
            {support.instagram && <a href={support.instagram} target="_blank" rel="noopener" style={{ opacity: 0.7, transition: "opacity .3s" }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.7}><NmhIconInstagram size={18} /></a>}
            {support.telegram && <a href={support.telegram} target="_blank" rel="noopener" style={{ opacity: 0.7, transition: "opacity .3s" }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.7}><NmhIconTelegram size={18} /></a>}
            {support.whatsapp && <a href={support.whatsapp} target="_blank" rel="noopener" style={{ opacity: 0.7, transition: "opacity .3s" }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.7}><NmhIconWhatsApp size={18} /></a>}
            {support.email && <a href={"mailto:" + support.email} style={{ opacity: 0.7, transition: "opacity .3s" }} onMouseEnter={e => e.currentTarget.style.opacity = 1} onMouseLeave={e => e.currentTarget.style.opacity = 0.7}><NmhIconEmail size={18} /></a>}
          </div>
        </div>
        <div><span style={{ fontFamily: C.sans, fontSize: "10px", letterSpacing: "3px", color: C.accent, display: "block", marginBottom: "14px" }}>Legal</span>{["terms", "privacy", "refund", "shipping", "payment"].map(k => <span key={k} style={{ fontFamily: C.sans, fontSize: "11px", color: C.sec, display: "block", marginBottom: "8px", cursor: "pointer" }}>{t.footer[k]}</span>)}</div>
      </div>
      <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: "20px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}><span style={{ fontFamily: C.sans, fontSize: "10px", color: C.muted }}>© 2024 NMH. {t.footer.rights}</span><div style={{ display: "flex", gap: "8px" }}>{["en", "ru", "es"].map(l => <span key={l} onClick={() => setLang(l)} style={{ fontFamily: C.sans, fontSize: "10px", textTransform: "uppercase", color: lang === l ? C.accent : C.muted, cursor: "pointer" }}>{l}</span>)}</div></div>
    </div></footer>;
  };

  // ROUTER
  const renderPage = () => {
    switch (page) {
      case "home": return <HomePage />;
      case "signature": return <CatPage items={PRODUCTS.signature} label={t.sigBlock.label} title={t.sigBlock.title} sub={t.sigBlock.sub} />;
      case "initiation": return <CatPage items={PRODUCTS.initiation} label="Initiation" title={t.houseStructure?.levels?.[1]?.name || "Initiation"} />;
      case "private": return <CatPage items={PRODUCTS.privateEditions} label={t.privateBlock.label} title={t.privateBlock.title} sub={t.privateBlock.sub} showCode />;
      case "ritual": return <CatPage items={PRODUCTS.ritualObjects} label={t.ritualBlock.label} title={t.ritualBlock.title} sub={t.ritualBlock.sub} />;
      case "product": return <ProductPage />;
      case "cart": return <CartPage />;
      case "checkout": return <CheckoutPage />;
      case "about": return <AboutPage />;
      case "faq": return <FaqPage />;
      case "journal": return <JournalPage />;
      case "support": return <SupportPage />;
      case "account": return <AccountPage />;
      case "orderStatus": return <OrderStatusPage />;
      default: return <HomePage />;
    }
  };

  

  return (
    <div>
      <Header />
      {toast && <div style={{ position: "fixed", bottom: "24px", left: "50%", transform: "translateX(-50%)", background: C.accent, color: C.bg, fontFamily: C.sans, fontSize: "11px", fontWeight: 600, letterSpacing: "2px", textTransform: "uppercase", padding: "10px 24px", zIndex: 2000, animation: "toastSlide .3s ease" }}>{toast}</div>}
      {renderPage()}
      <Footer />
      {/* Fragrance Finder floating trigger */}
      {showFinder && !finderActive && (
        <div style={{ position: "fixed", bottom: "32px", right: "32px", zIndex: 2500, animation: "toastSlide .5s ease" }}>
          <button onClick={() => { setFinderActive(true); setShowFinder(false); }} style={{ padding: "14px 28px", fontFamily: C.sans, fontSize: "11px", letterSpacing: "2px", textTransform: "uppercase", background: C.accent, color: C.bg, border: "none", cursor: "pointer", boxShadow: "0 8px 32px rgba(0,0,0,.4)", transition: "all .3s" }}>
            {lang === 'ru' ? 'Подобрать аромат' : lang === 'es' ? 'Encontrar tu aroma' : 'Find Your Scent'}
          </button>
          <span onClick={() => setShowFinder(false)} style={{ position: "absolute", top: "-8px", right: "-8px", width: "20px", height: "20px", background: C.bg, border: `1px solid ${C.border}`, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "10px", color: C.muted }}>x</span>
        </div>
      )}
      {/* Fragrance Finder full overlay quiz */}
      {finderActive && <FragranceFinder />}
    </div>
  );
}
