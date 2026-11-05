import asyncio,os,sys
from playwright.async_api import async_playwright
URL='file://'+os.path.abspath('games/path-quest/index.html')
S=sys.argv[1]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=4)
    await pg.goto(URL);await pg.wait_for_timeout(1500)
    sel=await pg.evaluate("()=>{const t=document.querySelector('#s-title');const l=t&&t.querySelector('.logo');return l?l.outerHTML.slice(0,200):'none'}")
    print(sel)
    await pg.evaluate("()=>{document.documentElement.style.background='transparent';document.body.style.background='transparent';const t=document.querySelector('#s-title');[...document.body.querySelectorAll('*')].forEach(e=>{if(!e.closest('.logo')&&!e.contains(document.querySelector('#s-title .logo')))e.style.visibility='hidden'});t.style.background='transparent';let e=document.querySelector('#s-title .logo');while(e&&e!==document.body){e.style.background='transparent';e.style.backgroundImage='none';e=e.parentElement}}")
    await pg.wait_for_timeout(300)
    await pg.locator('#s-title .logo').screenshot(path=S+'og_logo.png',omit_background=True)
    await b.close()
asyncio.run(main())
