on(construct){
   while(true)
   {
      if(!ord("\n"))
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push("\n");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownCenterSmallLabel";
         §§push("text");
         §§push("");
         if(false)
         {
            §§goto(addr16f00);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr16f00:
   getProperty(§§pop(), _X);
}
