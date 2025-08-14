(function(){
  // Fixed brand palette provided by user
  const BRAND_DARK = '#DA2128';
  const BRAND_MID  = '#ED6C30';
  const BRAND_LIGHT= '#EF5C28';

  document.documentElement.style.setProperty('--accent', BRAND_LIGHT);
  document.documentElement.style.setProperty('--accent2', BRAND_MID);
  document.documentElement.style.setProperty('--accent3', BRAND_DARK);

  const themeMeta = document.querySelector('meta[name="theme-color"]');
  if(themeMeta) themeMeta.setAttribute('content', BRAND_LIGHT);

  // Mark that a brand theme is applied (also hides the fallback circle via CSS rules)
  document.body.classList.add('has-logo');
})();
