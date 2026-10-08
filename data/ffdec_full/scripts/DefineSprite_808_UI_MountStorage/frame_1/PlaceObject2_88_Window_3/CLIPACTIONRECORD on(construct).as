on(construct){
   while(true)
   {
      if(!(0x81FEED & 0x81FEED))
      {
         if(!ord("\x0b"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(§§pop())
      {
         break;
      }
      set("\x16\x18\x14",false);
      contentPath = "none";
      enabled = true;
      set("\x18\f\t",false);
      styleName = "LightBrownWindow";
      §§push("title");
      §§push("");
      if(false)
      {
         §§goto(addr67d0);
      }
      break;
   }
   set(§§pop(),§§pop());
   addr67d0:
   new §\§\§pop()§();
}
