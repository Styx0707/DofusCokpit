on(construct){
   while(true)
   {
      if(!(0x03C704D9 & 0x03C704D9))
      {
         if(!(0x03C704D9 | 0x03C704D9))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 and _temp_1))
      {
         break;
      }
      if(!getTimer())
      {
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      }
      backgroundRenderer = "";
      set("\x16\x10\x12","");
      dragAndDrop = true;
      enabled = true;
      set("\x18\x07\x0e",true);
      §§push("highlightRenderer");
      §§push("ClassInfosViewerSpellContainerHighlight");
      if(!(getTimer() + 1))
      {
         §§goto(addr32d3f);
      }
      break;
   }
   set(§§pop(),§§pop());
   set("",1);
   set("",0);
   set("\x1d{invalid_utf8=150}\x07",false);
   set("\b\t\x01","");
   addr32d3f:
   getProperty(§§pop(), _X);
}
