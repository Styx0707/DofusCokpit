on(construct){
   while(true)
   {
      if(!(0x0ACA0979 & 0x0ACA0979))
      {
         if(!ord("\t"))
         {
            break;
         }
      }
      else
      {
         §§push("\t");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      set("\x16\x18\x14",false);
      contentPath = "none";
      enabled = true;
      set("\x18\f\t",false);
      §§push("styleName");
      §§push("LightBrownWindowNoTitle");
      if(!(getTimer() + 1))
      {
         §§goto(addr3df1a);
      }
      break;
   }
   set(§§pop(),§§pop());
   title = "";
   addr3df1a:
   getProperty(§§pop(), _X);
}
