on(construct){
   while(true)
   {
      if(!(0x188A1A4A & 0x188A1A4A))
      {
         if(!ord("\x0b"))
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      set("\x16\x18\x14",false);
      contentPath = "none";
      enabled = true;
      set("\x18\f\t",true);
      §§push("styleName");
      §§push("LightBrownCrafterListWindow");
      if(!(getTimer() + 1))
      {
         §§goto(addr4bc20);
      }
      break;
   }
   set(§§pop(),§§pop());
   title = "";
   addr4bc20:
   getProperty(§§pop(), _X);
}
