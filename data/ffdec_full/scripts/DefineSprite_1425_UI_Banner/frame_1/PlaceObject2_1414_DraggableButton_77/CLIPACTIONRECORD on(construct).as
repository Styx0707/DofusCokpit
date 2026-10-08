on(construct){
   while(true)
   {
      if(!(true and true))
      {
         if(!(true or true))
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(ord(§§pop()))
      {
         backgroundDown = "ButtonBannerRoundDown";
         backgroundUp = "ButtonBannerRoundUp";
         enabled = true;
         icon = "UI_BannerAchievementIcon";
         §§push("label");
         §§push("");
         if(!ord("\b"))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr244ec);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x1a\t\x14",false);
   selected = false;
   styleName = "none";
   toggle = false;
   addr244ec:
}
