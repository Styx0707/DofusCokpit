on(construct){
   while(true)
   {
      if(!ord("\x07"))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         set("\x16\x18\x14",false);
         contentPath = "none";
         enabled = true;
         set("\x18\f\t",false);
         §§push("styleName");
         §§push("LightBrownWindowNoTitle");
         if(false)
         {
            §§goto(addr2d5c);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   title = "";
   addr2d5c:
   getProperty(§§pop(), _X);
}
